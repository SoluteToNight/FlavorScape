<template>
  <main class="marketing-studio">
    <aside class="studio-sidebar">
      <div class="sidebar-header">
        <span class="eyebrow">Visual Workspace</span>
        <h2>风物海报工作室</h2>
        <p>规整高级色系矩阵，将空间地理数据转化为品牌价值资产。</p>
      </div>

      <div class="control-group">
        <div class="group-title">1. 选择核心作物资产</div>
        <div class="radio-cards">
          <button 
            v-for="item in products" :key="item.id" type="button"
            :class="{ active: activeProductId === item.id }" @click="handleProductChange(item)"
          >
            {{ item.name }}
          </button>
        </div>
      </div>

      <div class="control-group">
        <div class="group-title">2. 意象主图视觉资产</div>
        <div class="image-uploader-box">
          <label class="upload-stub-btn">
            {{ customImage ? '已应用本地实景 (点击更换)' : '上传自定义高清封面' }}
            <input type="file" accept="image/*" @change="onUserImageUpload" style="display:none;" />
          </label>
          <div v-if="customImage" class="slider-control">
            <span>垂直焦点位移调整</span>
            <input type="range" v-model="imagePosY" min="0" max="100" class="fine-tune-slider" />
          </div>
          <button v-if="customImage" class="reset-img-btn" @click="customImage = null; imagePosY = 50">恢复默认产品图</button>
        </div>
      </div>

      <div class="control-group">
        <div class="group-title">3. 切换高级视觉风格</div>
        <div class="radio-cards template-selector">
          <button 
            v-for="theme in themes" :key="theme.id" type="button"
            :class="{ active: activeThemeId === theme.id }" @click="activeThemeId = theme.id"
          >
            <strong>{{ theme.name }}</strong>
            <small>{{ theme.desc }}</small>
          </button>
        </div>
      </div>

      <div class="sidebar-footer">
        <button class="export-btn" :disabled="isExporting" @click="exportPoster">
          {{ isExporting ? '矩阵压制中...' : '输出海报资产 (PNG)' }}
        </button>
      </div>
    </aside>

    <section class="studio-stage">
      <article 
        id="poster-capture-zone" 
        class="marketing-poster"
        :class="[activeTheme.layout, activeTheme.typography]"
        :style="cssVariables"
      >
        <!-- 基础装饰线 -->
        <div class="canvas-hairline-frame"></div>

        <div class="poster-layout-container">
          <!-- 主图区域 -->
          <header class="poster-section-hero">
            <div class="hero-image-frame">
              <img 
                :src="customImage || product.image" 
                :alt="product.name" 
                class="visual-core-img"
                :style="{ objectPosition: 'center ' + imagePosY + '%' }" 
              />
              <div class="image-overlay" v-if="activeTheme.id === 'indigo'"></div>
            </div>
            
            <div class="hero-text-cluster">
              <div class="title-wrap">
                <span v-if="activeTheme.id === 'nature'" class="badge-tag">只做真实搬运 · 不做科技加工</span>
                <span v-if="activeTheme.id === 'heritage'" class="badge-tag seal">印</span>
                <h1 class="brand-title">{{ product.name }}</h1>
              </div>
              <p class="product-summary-desc">{{ product.desc }}</p>
              <div class="poetic-bar">{{ product.poeticLine }}</div>
            </div>
          </header>

          <!-- 叙事与地图区域 -->
          <section class="poster-section-narrative">
            <div class="narrative-text">
              <span class="geo-kicker">{{ activeTheme.kickerText }}</span>
              <h3>{{ activeTheme.subTitle }}</h3>
              <p v-html="formattedNarrative"></p>
            </div>
            <!-- 地图组件：通过CSS严格控制不遮挡 -->
            <div class="map-component-inner">
              <StaticGeoMap :target-province="product.province" :nodes="product.nodes" />
            </div>
          </section>

          <!-- 核心指标看板 (精简视觉噪音) -->
          <section class="poster-section-metrics">
            <div v-for="item in product.evidence" :key="item.label" class="metric-block">
              <span class="m-label">{{ item.label }}</span>
              <strong class="m-value">{{ item.value }}</strong>
            </div>
          </section>

          <footer class="poster-section-footer">
            <div class="footer-line"></div>
            <div class="copyright-info">
              <strong>FlavorScape 风物研究所</strong>
              <span>ORIGIN TRACKING & QUALITY VERIFICATION</span>
            </div>
            <div class="qr-stub"></div>
          </footer>
        </div>
      </article>
    </section>
  </main>
</template>

<script setup>
import { ref, computed } from 'vue'
import html2canvas from 'html2canvas'
import StaticGeoMap from '@/components/StaticGeoMap.vue'

// 1. 文案精简：去掉了啰嗦的说明，改为商业级短平快卖点
const products = [
  {
    id: 'pepper',
    name: '漢源花椒',
    province: '四川省',
    image: '/ingredients/pepper-realistic.png',
    desc: '大渡河干热河谷微气候 · 海拔1600米正路贡椒',
    poeticLine: '健康且好吃的食物，有趣且爱吃的朋友。', // 效仿参考图1的情绪文案
    narrative: '溯源于 <span class="hl">四川省</span>，经 <span class="hl">汉源 → 成都 → 上海</span> 全链路冷链直达。',
    nodes: [ 
      { short: '汉源', coord: [102.6342, 29.5621] },
      { short: '成都', coord: [104.1623, 30.8241] },
      { short: '上海', coord: [121.3821, 31.1123] }
    ],
    evidence: [
      { label: '芳香挥发油', value: '≥ 5.5%' },
      { label: '羟基山椒素', value: '≥ 35mg/g' },
      { label: '农残检测', value: '零检出' }
    ]
  },
  {
    id: 'rice',
    name: '五常大米',
    province: '黑龙江省',
    image: '/ingredients/rice-realistic.png',
    desc: '拉林河流域寒地黑土 · 140天单季熟成',
    poeticLine: '时间凝结的纯粹，出走半生归来仍是稻香。',
    narrative: '原产于 <span class="hl">黑龙江省</span>，经 <span class="hl">五常 → 哈尔滨 → 长三角</span> 锁鲜运送。',
    nodes: [
      { short: '五常', coord: [127.1676, 44.9192] },
      { short: '哈尔滨', coord: [126.6331, 45.7422] },
      { short: '长三角', coord: [121.4737, 31.2304] }
    ],
    evidence: [
      { label: '产地积温', value: '2700℃' },
      { label: '直链淀粉', value: '17.2%' },
      { label: '胶稠度', value: '≥ 70mm' }
    ]
  }
]

// 2. 视觉流派重构：颜色和排版彻底洗牌
const themes = [
  {
    id: 'nature',
    layout: 'layout-nature', 
    name: '极简绿 · 好食探索',
    desc: '高级农产品APP感。极度留白，纯净墨绿色。',
    typography: 'font-modern',
    kickerText: 'NATURE EXPLORATION',
    subTitle: '好食溯源',
    colors: { primary: '#2a4128', accent: '#708a68', bg: '#ffffff', paper: '#f4f5f2', text: '#333333' }
  },
  {
    id: 'heritage',
    layout: 'layout-heritage', 
    name: '古典米 · 东方风物',
    desc: '传统茶谱画册。竖向排版，错落分离无遮挡。',
    typography: 'font-classical',
    kickerText: 'ORIENTAL HERITAGE',
    subTitle: '山河空间志',
    colors: { primary: '#3c3127', accent: '#a1352a', bg: '#f6f3eb', paper: '#efe9dd', text: '#595045' }
  },
  {
    id: 'indigo', // 重命名，去科技化
    layout: 'layout-indigo', 
    name: '蓝染系 · 蓝印花布',
    desc: '非遗植物染肌理。粉笔白与深靛蓝，织物噪点。',
    typography: 'font-serif-modern',
    kickerText: 'CYANOTYPE PRINT',
    subTitle: '原产地拓印',
    colors: { primary: '#ffffff', accent: '#a6c6d9', bg: '#10223d', paper: '#19335a', text: '#dbeafe' }
  }
]

const activeProductId = ref('pepper')
const activeThemeId = ref('nature') // 默认换为自然绿
const isExporting = ref(false)
const imagePosY = ref(50) 
const customImage = ref(null)

const product = computed(() => products.find(p => p.id === activeProductId.value) || products[0])
const activeTheme = computed(() => themes.find(t => t.id === activeThemeId.value) || themes[0])
const formattedNarrative = computed(() => product.value.narrative)

function handleProductChange(item) { 
  activeProductId.value = item.id 
  customImage.value = null
  imagePosY.value = 50
}

function onUserImageUpload(e) {
  const file = e.target.files[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = (event) => { customImage.value = event.target.result }
  reader.readAsDataURL(file)
}

// 修复：针对蓝印风格，专门定制了地图配色的覆盖
const cssVariables = computed(() => {
  const isIndigo = activeTheme.value.id === 'indigo'
  const isNature = activeTheme.value.id === 'nature'
  
  return {
    '--t-primary': activeTheme.value.colors.primary,
    '--t-accent': activeTheme.value.colors.accent,
    '--t-bg': activeTheme.value.colors.bg,
    '--t-paper': activeTheme.value.colors.paper,
    '--t-text': activeTheme.value.colors.text,
    
    // 关键：地图图层颜色下发，蓝印花布用半透明白，绿色系用灰绿
    '--map-base-fill': isIndigo ? 'rgba(255,255,255,0.06)' : isNature ? '#eef1eb' : '#eae3d5',
    '--map-base-stroke': isIndigo ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.08)',
    '--map-active-fill': isIndigo ? '#ffffff' : activeTheme.value.colors.primary, 
    '--map-active-stroke': isIndigo ? '#10223d' : '#ffffff'
  }
})

async function exportPoster() {
  const target = document.querySelector('#poster-capture-zone')
  if (!target || isExporting.value) return
  isExporting.value = true
  try {
    const canvas = await html2canvas(target, { 
      scale: 3, 
      useCORS: true, 
      backgroundColor: activeTheme.value.colors.bg,
      logging: false 
    })
    const link = document.createElement('a')
    link.download = `flavorscape-poster-${activeTheme.value.id}.png`
    link.href = canvas.toDataURL('image/png', 1.0)
    link.click()
  } catch (err) { console.error(err) } finally { isExporting.value = false }
}
</script>

<style scoped>
/* ================= 工作台基础布局 (保持不变) ================= */
.marketing-studio { display: grid; grid-template-columns: 340px 1fr; height: calc(100vh - var(--navbar-h)); margin-top: var(--navbar-h); background: #dcd9d2; }
.studio-sidebar { background: #faf9f6; border-right: 1px solid rgba(0,0,0,0.08); padding: 32px 24px; display: flex; flex-direction: column; gap: 28px; overflow-y: auto; z-index: 20;}
.sidebar-header h2 { font-size: 19px; color: #1a1715; font-weight: 700; margin: 4px 0; }
.sidebar-header p { font-size: 12px; color: #6e6660; line-height: 1.5; }
.group-title { font-size: 11px; text-transform: uppercase; color: #8a8077; font-weight: 700; margin-bottom: 8px; letter-spacing: 0.05em; }
.radio-cards button { width: 100%; padding: 12px; border: 1px solid #dfdbd2; background: #fff; border-radius: 6px; text-align: left; margin-bottom: 8px; cursor: pointer; transition: all 0.2s; }
.radio-cards button.active { border-color: #b85433; background: rgba(184, 84, 51, 0.05); }
.template-selector button strong { display: block; font-size: 13px; color: #2a2320; }
.template-selector button.active strong { color: #b85433; }
.template-selector button small { font-size: 11px; color: #6e6660; display: block; margin-top: 3px; }
.image-uploader-box { background: #f4eee3; padding: 16px; border-radius: 6px; text-align: center; }
.upload-stub-btn { display: block; font-size: 12px; cursor: pointer; color: #b85433; font-weight: bold; margin-bottom: 8px; }
.fine-tune-slider { width: 100%; margin-bottom: 6px; }
.reset-img-btn { font-size: 11px; background: transparent; border: 1px solid #ccc; padding: 4px 8px; border-radius: 4px; cursor: pointer;}
.export-btn { width: 100%; padding: 14px; background: #201a17; color: #faf9f6; border: none; border-radius: 6px; font-weight: 700; cursor: pointer; margin-top: auto; }
.studio-stage { padding: 40px; overflow-y: auto; display: grid; place-items: start center; }

/* ================= 字体矩阵 ================= */
/* 现代无衬线 (自然绿适用) - 清爽、有机 */
.font-modern { font-family: "PingFang SC", "Helvetica Neue", -apple-system, sans-serif; }
/* 经典衬线 (古典米适用) - 人文、传统 */
.font-classical { font-family: "Noto Serif SC", "Songti SC", STSong, serif; }
/* 现代衬线结合 (蓝印适用) - 艺术、手工感 */
.font-serif-modern { font-family: "Optima", "Noto Serif SC", serif; }

/* ================= 海报通用基础 ================= */
.marketing-poster {
  width: 440px; min-height: 860px; 
  background-color: var(--t-bg); color: var(--t-text);
  box-shadow: 0 40px 80px rgba(0,0,0,0.15); 
  position: relative; overflow: hidden;
  transition: background-color 0.4s ease, color 0.4s ease;
}
.canvas-hairline-frame { position: absolute; inset: 16px; border: 1px solid var(--t-primary); opacity: 0.08; pointer-events: none; z-index: 10; }
.poster-layout-container { position: relative; z-index: 5; display: flex; flex-direction: column; min-height: 100%; padding: 40px 32px; gap: 32px; }

/* 基础图文 */
.hero-image-frame { position: relative; background: var(--t-paper); overflow: hidden; }
.visual-core-img { width: 100%; height: 100%; object-fit: cover; display: block; }
.brand-title { font-weight: 700; color: var(--t-primary); margin: 0; }
.product-summary-desc { font-size: 13px; opacity: 0.8; margin: 0; line-height: 1.5; }
.poetic-bar { font-size: 12px; font-style: italic; opacity: 0.7; }
.geo-kicker { font-size: 10px; text-transform: uppercase; letter-spacing: 0.1em; opacity: 0.5; font-family: sans-serif; display: block; margin-bottom: 4px; }

/* 通用 Footer */
.poster-section-footer { display: flex; justify-content: space-between; align-items: flex-end; margin-top: auto; padding-top: 24px; }
.footer-line { position: absolute; left: 32px; right: 32px; bottom: 85px; height: 1px; background: var(--t-primary); opacity: 0.15; }
.copyright-info strong { display: block; font-size: 12px; color: var(--t-primary); margin-bottom: 2px;}
.copyright-info span { font-size: 8px; opacity: 0.5; font-family: Arial, Helvetica, sans-serif; letter-spacing: 0.05em; }
.qr-stub { width: 36px; height: 36px; border: 1px solid var(--t-primary); opacity: 0.3; }

/* ================= 🌿 风格一：好食探索 (极简自然绿) ================= */
/* 核心美学：大面积纯净留白、模块化、无多余线条 */
.layout-nature .hero-image-frame { width: 100%; height: 320px; border-radius: 8px; box-shadow: 0 12px 24px rgba(42, 65, 40, 0.08); margin-bottom: 24px; }
.layout-nature .badge-tag { font-size: 10px; color: var(--t-primary); display: inline-block; margin-bottom: 12px; border-bottom: 1px solid var(--t-primary); padding-bottom: 2px; }
.layout-nature .brand-title { font-size: 36px; letter-spacing: 1px; margin-bottom: 12px; }
.layout-nature .poetic-bar { margin-top: 12px; font-style: normal; color: var(--t-accent); font-weight: 500; }
.layout-nature .poster-section-narrative { display: grid; grid-template-columns: 1fr 140px; gap: 24px; align-items: center; background: var(--t-paper); padding: 20px; border-radius: 8px; }
.layout-nature .narrative-text h3 { font-size: 15px; margin: 0 0 8px 0; color: var(--t-primary); }
.layout-nature .narrative-text p { font-size: 12px; line-height: 1.6; margin: 0; color: var(--t-text); }
.layout-nature :deep(.hl) { font-weight: bold; color: var(--t-primary); }
.layout-nature .map-component-inner { height: 120px; }
.layout-nature .poster-section-metrics { display: flex; gap: 12px; }
.layout-nature .metric-block { flex: 1; padding: 12px 0; text-align: left; border-top: 1px solid rgba(0,0,0,0.06); }
.layout-nature .m-label { font-size: 10px; margin-bottom: 4px; }
.layout-nature .m-value { font-size: 15px; color: var(--t-primary); }

/* ================= 📜 风格二：东方风物 (古典米色) ================= */
/* 核心美学：竖向排版、印章点缀、彻底分离防遮挡 */
.layout-heritage { padding: 10px; }
.layout-heritage .poster-layout-container { border: 1px solid rgba(60,49,39,0.2); padding: 36px 24px; background: url('https://www.transparenttextures.com/patterns/rice-paper.png'); }
.layout-heritage .poster-section-hero { display: flex; flex-direction: row-reverse; justify-content: space-between; align-items: flex-start; }
.layout-heritage .hero-image-frame { width: 180px; height: 260px; border-radius: 200px 200px 0 0; padding: 4px; border: 1px solid rgba(60,49,39,0.3); }
.layout-heritage .visual-core-img { border-radius: 196px 196px 0 0; }
.layout-heritage .hero-text-cluster { display: flex; flex-direction: row-reverse; writing-mode: vertical-rl; height: 260px; align-items: flex-start; }
.layout-heritage .brand-title { font-size: 42px; font-weight: 500; letter-spacing: 0.1em; color: var(--t-primary); }
.layout-heritage .seal { display: inline-block; width: 24px; height: 24px; background: var(--t-accent); color: #fff; text-align: center; line-height: 24px; border-radius: 2px; font-size: 12px; margin-bottom: 12px; writing-mode: horizontal-tb; }
.layout-heritage .product-summary-desc { font-size: 13px; letter-spacing: 0.1em; margin-right: 16px; opacity: 0.9; }
.layout-heritage .poetic-bar { font-size: 12px; margin-right: 12px; padding-right: 8px; border-right: 1px solid var(--t-accent); }

/* 重点：地图完全放入底部独立盒子，彻底解决重叠 */
.layout-heritage .poster-section-narrative { margin-top: 24px; display: flex; flex-direction: column; gap: 16px; }
.layout-heritage .narrative-text { text-align: center; border-bottom: 1px dashed rgba(60,49,39,0.2); padding-bottom: 16px; }
.layout-heritage .narrative-text h3 { font-size: 18px; margin: 0 0 8px 0; font-weight: 500; }
.layout-heritage .narrative-text p { font-size: 12px; opacity: 0.8; margin: 0; }
.layout-heritage :deep(.hl) { color: var(--t-accent); font-weight: bold; }
.layout-heritage .map-component-inner { width: 100%; height: 200px; }

.layout-heritage .poster-section-metrics { display: flex; justify-content: center; gap: 32px; margin-top: 16px; }
.layout-heritage .metric-block { text-align: center; }
.layout-heritage .m-label { font-size: 10px; color: var(--t-text); margin-bottom: 6px; }
.layout-heritage .m-value { font-size: 16px; color: var(--t-accent); font-weight: bold; }

/* ================= 🧵 风格三：蓝印花布 (非遗蓝染) ================= */
/* 核心美学：SVG噪点布纹肌理、深靛蓝、粉笔白、手工感框线 */
.layout-indigo { 
  /* SVG Fractal Noise: 制造布面噪点肌理 */
  position: relative;
}
.layout-indigo::before {
  content: ''; position: absolute; inset: 0; z-index: 1; pointer-events: none; mix-blend-mode: overlay; opacity: 0.4;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E");
}

.layout-indigo .canvas-hairline-frame { border: 2px solid var(--t-primary); opacity: 0.8; inset: 20px; border-radius: 4px; }
.layout-indigo .poster-layout-container { padding: 48px 40px; }
.layout-indigo .hero-image-frame { width: 100%; height: 220px; border: 4px solid var(--t-primary); position: relative; }
/* 给蓝染图片加上一层深蓝混合模式，模拟蓝色相纸印出来的感觉 */
.layout-indigo .image-overlay { position: absolute; inset: 0; background: var(--t-bg); mix-blend-mode: screen; opacity: 0.5; pointer-events: none; }
.layout-indigo .visual-core-img { filter: grayscale(100%) contrast(120%); }

.layout-indigo .hero-text-cluster { margin-top: 24px; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.3); padding-bottom: 24px; }
.layout-indigo .brand-title { font-size: 38px; letter-spacing: 4px; margin-bottom: 12px; text-shadow: 0 2px 4px rgba(0,0,0,0.3); }
.layout-indigo .poetic-bar { margin-top: 8px; color: var(--t-accent); }

.layout-indigo .poster-section-narrative { position: relative; margin-top: 12px; }
.layout-indigo .narrative-text { position: absolute; top: 0; left: 0; right: 0; z-index: 2; text-align: center; text-shadow: 0 2px 8px rgba(16,34,61, 0.8); }
.layout-indigo .narrative-text h3 { font-size: 16px; margin: 0 0 6px 0; color: var(--t-accent); letter-spacing: 2px; }
.layout-indigo .narrative-text p { font-size: 12px; margin: 0; }
.layout-indigo :deep(.hl) { color: #ffffff; text-decoration: underline; text-decoration-color: var(--t-accent); text-underline-offset: 4px; }
.layout-indigo .map-component-inner { width: 100%; height: 240px; margin-top: 40px; opacity: 0.9; }

.layout-indigo .poster-section-metrics { display: flex; gap: 8px; }
.layout-indigo .metric-block { flex: 1; border: 1px solid rgba(255,255,255,0.3); padding: 12px 8px; text-align: center; background: rgba(25, 51, 90, 0.4); backdrop-filter: blur(4px); }
.layout-indigo .m-label { font-size: 9px; color: var(--t-accent); }
.layout-indigo .m-value { font-size: 14px; margin-top: 4px; display: block; }
</style>