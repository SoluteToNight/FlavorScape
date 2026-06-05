<template>
  <article class="archive-canvas" :style="{ transform: `scale(${scale})`, transformOrigin: 'top left' }">
    <header class="archive-head">
      <span>PROVENANCE DOSSIER</span>
      <h1>{{ archiveData.title }}</h1>
      <p>{{ archiveData.summary }}</p>
    </header>

    <section v-if="showArchiveGrid" class="archive-grid">
      <div v-if="archiveData.modules?.spatialBase !== false && archiveData.spatial.nodes?.length" class="map-card">
        <h2>空间底板</h2>
        <div class="map-shell">
          <StaticGeoMap :target-province="archiveData.province" :nodes="archiveData.spatial.nodes" />
        </div>
      </div>
      <div v-else-if="archiveData.modules?.spatialBase !== false && archiveData.sourceAsset" class="map-card missing-map-card">
        <h2>空间底板</h2>
        <strong>待补齐坐标</strong>
        <p>当前白皮书来自 DeepSeek 资产包，但资产包没有可投影的 map_nodes 坐标，因此不使用默认案例地图。</p>
        <ul v-if="archiveData.spatial.unmappedNodes?.length">
          <li v-for="item in archiveData.spatial.unmappedNodes.slice(0, 4)" :key="item.name">
            {{ item.name }} / {{ item.reason }}
          </li>
        </ul>
      </div>
      <div v-if="archiveData.modules?.originInfo !== false" class="fact-card">
        <h2>产地信息</h2>
        <dl>
          <div>
            <dt>产品</dt>
            <dd v-if="archiveData.productName">{{ archiveData.productName }}</dd>
            <dd v-else class="skeleton-line" aria-label="产品待生成" />
          </div>
          <div v-if="archiveData.origin">
            <dt>产地</dt>
            <dd>{{ archiveData.origin }}</dd>
          </div>
          <div v-if="archiveData.category">
            <dt>品类</dt>
            <dd>{{ archiveData.category }}</dd>
          </div>
        </dl>
      </div>
    </section>

    <section v-if="archiveData.citations?.length" class="citation-section">
      <h2>引用定位</h2>
      <div class="citation-row">
        <div v-for="item in archiveData.citations.slice(0, 3)" :key="item.id || item.claim">
          <span v-if="citationMeta(item)">{{ citationMeta(item) }}</span>
          <strong>{{ item.claim || '证据引用' }}</strong>
          <p v-if="item.quote">{{ item.quote }}</p>
          <p v-else class="skeleton-copy" aria-label="引用摘录待生成" />
        </div>
      </div>
    </section>

    <section v-if="archiveData.modules?.evidenceMetrics !== false" class="evidence-section">
      <h2>核心证据指标</h2>
      <div v-if="validEvidence.length" class="evidence-row">
        <div v-for="item in validEvidence" :key="item.label">
          <span>{{ item.label }}</span>
          <strong>{{ item.value }}</strong>
        </div>
      </div>
      <p v-else class="evidence-placeholder">风味实证指标正在测算中...</p>
    </section>

    <section v-if="archiveData.reviewStatus" class="review-section">
      <h2>人工复核状态</h2>
      <strong>{{ reviewLabel }}</strong>
      <p>{{ archiveData.reviewStatus.summary || '证据尚未人工复核。' }}</p>
    </section>

    <section v-if="archiveData.modules?.nodeLinks !== false && archiveData.spatial.nodes?.length" class="node-section">
      <h2>空间节点链路</h2>
      <div class="node-list">
        <div v-for="(node, index) in archiveData.spatial.nodes" :key="node.short">
          <span>0{{ index + 1 }}</span>
          <strong>{{ node.short }}</strong>
          <p>{{ node.desc }}</p>
        </div>
      </div>
    </section>

    <footer v-if="archiveData.modules?.conclusion !== false && archiveData.conclusion">
      <strong>结论</strong>
      <p>{{ archiveData.conclusion }}</p>
    </footer>
  </article>
</template>

<script setup>
import { computed } from 'vue'
import StaticGeoMap from './StaticGeoMap.vue'

const props = defineProps({
  archiveData: { type: Object, required: true },
  scale: { type: Number, default: 1 },
})

const showArchiveGrid = computed(() =>
  (props.archiveData.modules?.spatialBase !== false && Boolean(props.archiveData.spatial.nodes?.length))
  || (props.archiveData.modules?.spatialBase !== false && Boolean(props.archiveData.sourceAsset))
  || props.archiveData.modules?.originInfo !== false
)

const validEvidence = computed(() =>
  (props.archiveData.evidence || []).filter(item => {
    const value = item?.value
    if (value === null || value === undefined) return false
    return String(value).trim().toLowerCase() !== 'pending'
  })
)

const reviewLabel = computed(() => {
  const labels = {
    pending: '等待人工复核',
    needs_review: '需要重点复核',
    in_review: '复核进行中',
    approved: '已复核通过',
    rejected: '复核未通过',
  }
  return labels[props.archiveData.reviewStatus?.status] || '等待人工复核'
})

function citationMeta(item) {
  return [item.source, item.locator].filter(Boolean).join(' · ')
}
</script>

<style scoped>
.archive-canvas {
  width: 760px;
  height: auto !important;
  min-height: 297mm;
  overflow: visible;
  background: #fbfaf6;
  color: #201b16;
  padding: 44px 44px 40px;
  box-shadow: 0 38px 80px rgba(0,0,0,0.16);
}

.archive-head {
  border-bottom: 2px solid rgba(32,27,22,0.12);
  padding-bottom: 24px;
}

.archive-head span {
  color: #8b5e34;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.16em;
}

h1,
h2,
p {
  margin: 0;
}

h1 {
  margin-top: 8px;
  font-family: var(--font-serif);
  font-size: 34px;
  font-weight: 600;
}

.archive-head p {
  margin-top: 12px;
  color: #5c5147;
  font-size: 14px;
  line-height: 1.8;
}

h2 {
  font-size: 13px;
  letter-spacing: 0.08em;
  color: #8b5e34;
}

.archive-grid {
  display: flex;
  align-items: stretch;
  gap: 18px;
  margin-top: 26px;
  min-width: 0;
}

.map-card,
.fact-card,
.evidence-section,
.node-section,
footer {
  border: 1px solid rgba(118,96,68,0.18);
  background: #fffdf8;
  padding: 18px;
}

.map-card,
.fact-card {
  flex: 1;
  min-width: 0;
}

.map-card {
  position: relative;
  height: 250px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.map-shell {
  position: relative;
  flex: 1;
  min-height: 0;
  width: 100%;
  max-height: 205px;
  height: 195px;
  margin-top: 10px;
  overflow: hidden;
  display: grid;
  place-items: center;
}

.map-shell :deep(.static-geo-map),
.map-shell :deep(svg),
.map-shell :deep(canvas),
.map-shell :deep(div) {
  width: 100% !important;
  height: 100% !important;
  max-height: 205px;
  object-fit: contain;
}

.map-shell :deep(svg) {
  overflow: hidden !important;
}

.missing-map-card {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.missing-map-card strong {
  display: block;
  margin-top: 18px;
  color: #201b16;
  font-size: 20px;
}

.missing-map-card p,
.missing-map-card li {
  color: #5c5147;
  font-size: 12px;
  line-height: 1.65;
}

.missing-map-card p {
  margin-top: 10px;
}

.missing-map-card ul {
  display: grid;
  gap: 4px;
  margin: 10px 0 0;
  padding-left: 16px;
}

dl {
  margin: 14px 0 0;
  display: grid;
  gap: 14px;
}

dt {
  color: #9f968b;
  font-size: 10px;
}

dd {
  margin: 4px 0 0;
  font-size: 15px;
  font-weight: 700;
  overflow-wrap: anywhere;
}

.skeleton-line,
.skeleton-copy {
  display: block;
  border-radius: 999px;
  background: linear-gradient(90deg, rgba(32,27,22,0.06), rgba(32,27,22,0.12), rgba(32,27,22,0.06));
  background-size: 180% 100%;
  animation: skeleton-shimmer 1.2s ease-in-out infinite;
}

.skeleton-line {
  width: 72%;
  height: 16px;
}

.skeleton-copy {
  width: 100%;
  height: 38px;
  border-radius: 6px;
}

.evidence-section,
.node-section,
.citation-section,
.review-section,
footer {
  margin-top: 18px;
}

.evidence-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-top: 14px;
}

.citation-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-top: 14px;
}

.evidence-row div,
.node-list div,
.citation-row div {
  border-top: 1px solid rgba(32,27,22,0.1);
  padding-top: 12px;
}

.evidence-row span,
.node-list span,
.citation-row span {
  display: block;
  color: #9f968b;
  font-size: 10px;
}

.evidence-row strong {
  display: block;
  margin-top: 8px;
  font-family: var(--font-serif);
  font-size: 22px;
}

.evidence-placeholder {
  margin-top: 14px;
  border: 1px dashed rgba(118,96,68,0.22);
  border-radius: 6px;
  background: rgba(246, 243, 235, 0.56);
  color: #8a7f72;
  font-size: 13px;
  line-height: 1.7;
  padding: 14px;
}

.node-list {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-top: 14px;
}

.node-list strong {
  display: block;
  margin-top: 8px;
  font-size: 16px;
}

.citation-row strong {
  display: block;
  margin-top: 7px;
  font-size: 13px;
}

.node-list p,
.citation-row p,
.review-section p,
footer p {
  margin-top: 8px;
  color: #5c5147;
  font-size: 12px;
  line-height: 1.7;
}

.review-section strong {
  display: block;
  margin-top: 10px;
  color: #8b5e34;
  font-size: 15px;
}

footer {
  display: grid;
  grid-template-columns: 80px 1fr;
  gap: 18px;
}

@keyframes skeleton-shimmer {
  0% { background-position: 100% 0; }
  100% { background-position: -100% 0; }
}
</style>
