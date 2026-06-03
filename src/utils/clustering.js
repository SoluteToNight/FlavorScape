/**
 * 地理空间聚类工具 — 基于 Haversine 大圆距离的 Union-Find 聚类
 *
 * 用于在 Deck.gl 层和 DOM 气泡之间共享一致的聚类结果。
 * 所有距离计算均基于 EPSG:4326 地理坐标（度数）。
 */

const EARTH_RADIUS_KM = 6371

/** 度数转弧度 */
function toRad(deg) {
  return (deg * Math.PI) / 180
}

/**
 * Haversine 大圆距离 (km)
 * @param {[number, number]} a — [lng, lat]
 * @param {[number, number]} b — [lng, lat]
 * @returns {number} 两点间距离（千米）
 */
export function haversineDistance(a, b) {
  const dLat = toRad(b[1] - a[1])
  const dLng = toRad(b[0] - a[0])
  const sinDLat = Math.sin(dLat / 2)
  const sinDLng = Math.sin(dLng / 2)
  const latA = toRad(a[1])
  const latB = toRad(b[1])
  const h =
    sinDLat * sinDLat + Math.cos(latA) * Math.cos(latB) * sinDLng * sinDLng
  return 2 * EARTH_RADIUS_KM * Math.asin(Math.sqrt(h))
}

/**
 * 根据缩放级别返回聚类距离阈值 (km)
 *
 * 与现有 DOM 气泡聚类 (MapView.vue getClusterDistance) 阈值对齐:
 *   zoom < 3.4   → 强聚合（跨省大群）
 *   zoom 3.4–4.15 → 中等聚合（相邻城市）
 *   zoom ≥ 4.15  → 无聚合（全部独立）
 *
 * @param {number} zoom — 地图缩放级别
 * @returns {number} 距离阈值 (km)，0 表示不聚合
 */
export function getClusterDistanceKm(zoom) {
  if (zoom < 3.4) return 800
  if (zoom < 4.15) return 400
  return 0
}

/**
 * 聚合透明度插值 — 用于图层淡入淡出
 *
 * zoom < 3.4:  1.0（聚合图层完全可见）
 * zoom 3.4–4.15: 1.0 → 0 线性（平滑过渡）
 * zoom ≥ 4.15: 0（聚合图层完全隐藏）
 *
 * @param {number} zoom
 * @returns {number} 0..1
 */
export function getClusterOpacity(zoom) {
  if (zoom < 3.4) return 1
  if (zoom >= 4.15) return 0
  return 1 - (zoom - 3.4) / (4.15 - 3.4)
}

/**
 * Union-Find (Disjoint Set Union) 辅助
 */
class UnionFind {
  constructor(n) {
    this.parent = Array.from({ length: n }, (_, i) => i)
    this.rank = new Array(n).fill(0)
  }

  find(x) {
    if (this.parent[x] !== x) {
      this.parent[x] = this.find(this.parent[x])
    }
    return this.parent[x]
  }

  union(x, y) {
    const rx = this.find(x)
    const ry = this.find(y)
    if (rx === ry) return
    if (this.rank[rx] < this.rank[ry]) {
      this.parent[rx] = ry
    } else if (this.rank[rx] > this.rank[ry]) {
      this.parent[ry] = rx
    } else {
      this.parent[ry] = rx
      this.rank[rx]++
    }
  }
}

/**
 * 球面地理质心 — 将成员坐标转为 3D 笛卡尔坐标后取均值，再投影回球面。
 *
 * 比算术平均经纬度更精确，特别适合跨度较大的聚类群（800 km 阈值）。
 * 仅当 members.length >= 2 时调用；单个成员直接取其坐标即可。
 *
 * @param {Array} members — 风味节点数组，每个 node 有 coordinates: [lng, lat]
 * @returns {[number, number]} 球面质心 [lng, lat]
 */
function sphericalCentroid(members) {
  let x = 0, y = 0, z = 0
  for (const m of members) {
    const [lng, lat] = m.coordinates
    const phi = toRad(lat)
    const theta = toRad(lng)
    x += Math.cos(phi) * Math.cos(theta)
    y += Math.cos(phi) * Math.sin(theta)
    z += Math.sin(phi)
  }
  const norm = Math.sqrt(x * x + y * y + z * z)
  if (norm < 1e-9) {
    // 极端情况（所有向量互相抵消）：回退到算术平均
    return [
      members.reduce((s, m) => s + m.coordinates[0], 0) / members.length,
      members.reduce((s, m) => s + m.coordinates[1], 0) / members.length,
    ]
  }
  // clamp 防止浮点精度导致 Math.asin 返回 NaN（如 1.0000000000000002）
  const t = Math.max(-1, Math.min(1, z / norm))
  const lng = Math.atan2(y, x) * (180 / Math.PI)
  const lat = Math.asin(t) * (180 / Math.PI)
  return [lng, lat]
}

/**
 * 对风味节点执行地理空间聚类
 *
 * @param {Array} flavors — 风味节点数组，每个节点需有 id 和 coordinates: [lng, lat]
 * @param {number} zoom — 当前缩放级别
 * @returns {{ clusters: Array, clusterMap: Map<string, string|null>, unclusteredFlavors: Array }}
 *   - clusters: [{ id, center: [lng,lat], members: [Flavor], count }]
 *   - clusterMap: Map<flavorId, clusterId | null> — null 表示未聚类
 *   - unclusteredFlavors: 未加入任何聚类的风味节点数组
 */
export function computeClusters(flavors, zoom) {
  const threshold = getClusterDistanceKm(zoom)

  if (!threshold || flavors.length <= 1) {
    return {
      clusters: [],
      clusterMap: new Map(flavors.map(f => [f.id, null])),
      unclusteredFlavors: [...flavors],
    }
  }

  const n = flavors.length
  const uf = new UnionFind(n)

  // 对所有 (i, j) 对计算距离并合并 — O(n²)
  // 当前节点数 ~17（136 次比较），开销可忽略。
  // 当节点数超过 ~200 时，应考虑用网格分桶或 k-d 树做空间预筛选。
  for (let i = 0; i < n; i++) {
    for (let j = i + 1; j < n; j++) {
      if (haversineDistance(flavors[i].coordinates, flavors[j].coordinates) <= threshold) {
        uf.union(i, j)
      }
    }
  }

  // 按根节点分组
  const groups = new Map()
  for (let i = 0; i < n; i++) {
    const root = uf.find(i)
    if (!groups.has(root)) groups.set(root, [])
    groups.get(root).push(flavors[i])
  }

  const clusters = []
  const clusterMap = new Map()
  const unclusteredFlavors = []

  for (const members of groups.values()) {
    if (members.length === 1) {
      clusterMap.set(members[0].id, null)
      unclusteredFlavors.push(members[0])
      continue
    }

    // 球面地理质心（比算术平均更精确）
    const center = sphericalCentroid(members)

    // 防御：若质心为 NaN（极端浮点精度问题），回退到算术平均
    if (isNaN(center[0]) || isNaN(center[1])) {
      center[0] = members.reduce((s, m) => s + m.coordinates[0], 0) / members.length
      center[1] = members.reduce((s, m) => s + m.coordinates[1], 0) / members.length
    }

    // 集群 id：所有成员 id 排序后以 - 连接
    const sortedIds = members.map(m => m.id).sort()
    const id = `cluster-${sortedIds.join('-')}`

    // 主色：取第一个成员的颜色
    const dominantColor = members[0].color

    clusters.push({ id, center, members, count: members.length, dominantColor })

    for (const m of members) {
      clusterMap.set(m.id, id)
    }
  }

  return { clusters, clusterMap, unclusteredFlavors }
}
