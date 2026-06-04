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
            v-for="item in products"
            :key="item.id"
            type="button"
            :class="{ active: activeProductId === item.id }"
            @click="handleProductChange(item)"
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
            <input v-model="imagePosY" type="range" min="0" max="100" class="fine-tune-slider" />
          </div>
          <button v-if="customImage" class="reset-img-btn" @click="customImage = null; imagePosY = 50">恢复默认产品图</button>
        </div>
      </div>

      <div class="control-group">
        <div class="group-title">3. 切换高级视觉风格</div>
        <div class="radio-cards template-selector">
          <button
            v-for="theme in themes"
            :key="theme.id"
            type="button"
            :class="{ active: activeThemeId === theme.id }"
            @click="activeThemeId = theme.id"
          >
            <strong>{{ theme.name }}</strong>
            <small>{{ theme.desc }}</small>
          </button>
        </div>
      </div>

      <div class="control-group">
        <div class="group-title">4. 编辑海报文案</div>
        <div class="copy-editor">
          <label>
            <span>标题</span>
            <input v-model="activeDraft.title" type="text" />
          </label>
          <label>
            <span>产品卖点</span>
            <textarea v-model="activeDraft.desc" rows="3"></textarea>
          </label>
          <label>
            <span>情绪短句</span>
            <textarea v-model="activeDraft.poeticLine" rows="2"></textarea>
          </label>
          <label>
            <span>溯源叙事</span>
            <textarea v-model="activeDraft.narrative" rows="4"></textarea>
          </label>
          <label>
            <span>复制用营销文案</span>
            <textarea v-model="activeDraft.marketingCopy" rows="4"></textarea>
          </label>
          <button type="button" class="reset-copy-btn" @click="resetActiveDraft">恢复默认文案</button>
        </div>
      </div>

      <div class="sidebar-footer">
        <button class="export-btn" :disabled="isExporting" @click="exportPoster">
          {{ isExporting ? '矩阵压制中...' : '导出 PNG' }}
        </button>
        <button class="copy-btn" type="button" @click="copyMarketingCopy">
          {{ copyStatus || '复制文案' }}
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
        <div class="canvas-hairline-frame"></div>

        <div class="poster-layout-container">
          <header class="poster-section-hero">
            <div class="hero-image-frame">
              <img
                :src="customImage || product.image"
                :alt="product.name"
                class="visual-core-img"
                :style="{ objectPosition: 'center ' + imagePosY + '%' }"
              />
              <div v-if="activeTheme.id === 'indigo'" class="image-overlay"></div>
            </div>

            <div class="hero-text-cluster">
              <div class="title-wrap">
                <span v-if="activeTheme.id === 'nature'" class="badge-tag">只做真实搬运 · 不做科技加工</span>
                <span v-if="activeTheme.id === 'heritage'" class="badge-tag seal">印</span>
                <h1 class="brand-title">{{ posterText.title }}</h1>
              </div>
              <p class="product-summary-desc">{{ posterText.desc }}</p>
              <div class="poetic-bar">{{ posterText.poeticLine }}</div>
            </div>
          </header>

          <section class="poster-section-narrative">
            <div class="narrative-text">
              <span class="geo-kicker">{{ activeTheme.kickerText }}</span>
              <h3>{{ activeTheme.subTitle }}</h3>
              <p v-html="formattedNarrative"></p>
            </div>
            <div class="map-component-inner">
              <StaticGeoMap :target-province="product.province" :nodes="product.nodes" />
            </div>
          </section>

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
import { ref, computed, reactive } from 'vue'
import html2canvas from 'html2canvas'
import StaticGeoMap from '@/components/StaticGeoMap.vue'

const products = [
  {
    id: 'pepper',
    name: '漢源花椒',
    category: '地理标志调味物',
    brandScenario: '精品餐饮、复合调味、地方风味伴手礼',
    province: '四川省',
    image: '/cases/cover-pepper.jpg',
    desc: '大渡河干热河谷微气候 · 海拔1600米正路贡椒',
    poeticLine: '健康且好吃的食物，有趣且爱吃的朋友。',
    narrative: '溯源于 <span class="hl">四川省</span>，经 <span class="hl">汉源 → 成都 → 上海</span> 全链路冷链直达。',
    marketInsight: '花椒从地方调味品转向标准化风味资产，用户需要的是可感知的麻香等级、产地真实性和稳定供应。',
    marketingCopy: '从大渡河谷的阳光和海拔里摘下麻香，用一条可视化链路证明每一粒花椒的来处。',
    craftBadge: '干热河谷 · 麻香分级',
    craftTitle: '一粒贡椒的麻香路径',
    craftSubtitle: '从采摘、晾晒到分级直达',
    nodes: [
      { short: '汉源', coord: [102.6342, 29.5621] },
      { short: '成都', coord: [104.1623, 30.8241] },
      { short: '上海', coord: [121.3821, 31.1123] }
    ],
    evidence: [
      { label: '芳香挥发油', value: '≥ 5.5%' },
      { label: '羟基山椒素', value: '≥ 35mg/g' },
      { label: '农残检测', value: '零检出' }
    ],
    craftsmanship: [
      { title: '河谷采摘', tag: 'ORIGIN', desc: '高海拔干热河谷成熟采收，保留青红转熟期的麻香张力。' },
      { title: '低温晾晒', tag: 'DRYING', desc: '控制含水率与裂口状态，让香气不被高温粗暴带走。' },
      { title: '麻香分级', tag: 'GRADE', desc: '按挥发油、色泽和颗粒完整度分级，形成可复制的餐饮采购标准。' }
    ]
  },
  {
    id: 'rice',
    name: '五常大米',
    category: '寒地黑土主粮',
    brandScenario: '高端家庭餐桌、礼盒、连锁米饭供应链',
    province: '黑龙江省',
    image: '/cases/cover-rice.jpg',
    desc: '拉林河流域寒地黑土 · 140天单季熟成',
    poeticLine: '时间凝结的纯粹，出走半生归来仍是稻香。',
    narrative: '原产于 <span class="hl">黑龙江省</span>，经 <span class="hl">五常 → 哈尔滨 → 长三角</span> 锁鲜运送。',
    marketInsight: '主粮消费正在从“便宜大包装”转向“产地、品种、食味值”的组合证明。',
    marketingCopy: '把黑土、积温和单季熟成讲清楚，五常米才不只是一个地名，而是一套可信的风味证据。',
    craftBadge: '寒地黑土 · 单季熟成',
    craftTitle: '一碗米饭的黑土证据',
    craftSubtitle: '从育秧到锁鲜精米',
    nodes: [
      { short: '五常', coord: [127.1676, 44.9192] },
      { short: '哈尔滨', coord: [126.6331, 45.7422] },
      { short: '长三角', coord: [121.4737, 31.2304] }
    ],
    evidence: [
      { label: '产地积温', value: '2700℃' },
      { label: '直链淀粉', value: '17.2%' },
      { label: '胶稠度', value: '≥ 70mm' }
    ],
    craftsmanship: [
      { title: '春季育秧', tag: 'SEED', desc: '寒地春耕窗口短，秧苗质量决定整季稻米的生长底子。' },
      { title: '单季熟成', tag: 'SEASON', desc: '140 天慢熟积累淀粉结构和米香，不追求多季快速产出。' },
      { title: '锁鲜精米', tag: 'MILL', desc: '精米加工后控制流通时效，减少香气和口感在运输中的损耗。' }
    ]
  },
  {
    id: 'jasmine_tea_base',
    name: '七窨茉莉翠芽茶底',
    category: '新式茶饮茶底',
    brandScenario: '新国风茶饮、纯茶基底、联名茶饮研发',
    province: '广西壮族自治区',
    image: '/cases/cover-jasmine.jpg',
    desc: '福建茶骨与广西夏夜花香 · 七次窨制成一杯纯茶底',
    poeticLine: '看不见一朵花，却咽不下整座春天的香。',
    narrative: '福建宁德茶坯抵达 <span class="hl">广西横县</span>，经 <span class="hl">茶坯 → 花源 → 窨制 → 供应链仓 → 门店</span> 完成新式茶饮茶底链路。',
    marketInsight: '新国风茶饮的尽头是茶汤纯正度。年轻消费者开始为“几窨工艺”和“纯茶无香精”买单。',
    marketingCopy: '历经七次换花、168小时昼夜不眠的窨制，让福建的茶骨，彻底融进广西横县的夏夜花香。',
    craftBadge: '七窨 · 非遗窨制',
    craftTitle: '两千公里，七次生死交融的窨制',
    craftSubtitle: '茶坯与鲜花的双城风味叙事',
    nodes: [
      { short: '福建茶坯', coord: [119.5479, 27.2489] },
      { short: '横县花源', coord: [109.2679, 22.6799] },
      { short: '窨制工坊', coord: [109.2458, 22.6874] },
      { short: '东莞仓', coord: [113.7518, 23.0207] },
      { short: '茶饮门店', coord: [121.4737, 31.2304] }
    ],
    evidence: [
      { label: '窨制周期', value: '近20天' },
      { label: '换花次数', value: '7次' },
      { label: '香气证据', value: 'GC-MS' }
    ],
    craftsmanship: [
      {
        title: '两千公里的双向奔赴',
        image: '/cases/jasmine-craft-1.jpg',
        tag: 'ROUTE',
        desc: '清明前采摘的福建高山绿茶运抵广西横县，静待夏日盛放的茉莉。'
      },
      {
        title: '午后伏天采花',
        image: '/cases/jasmine-craft-2.jpg',
        tag: 'FLOWER',
        desc: '只采晴天午后 2 点到 4 点的当天欲开伏花，此时精油浓度达到高峰。'
      },
      {
        title: '夜间堆窨与伺花',
        image: '/cases/jasmine-craft-3.jpg',
        tag: 'NIGHT',
        desc: '深夜茉莉微开呈虎爪状，茶坯与鲜花层层叠放，并多次通花散热。'
      },
      {
        title: '七窨一生',
        tag: 'SEVEN',
        desc: '每窨一次筛除旧花并更换鲜花，近 20 天反复循环，方得只闻花香不见花影。'
      }
    ]
  },
  {
    id: 'wenchang_coconut',
    name: '文昌生椰',
    category: '新消费饮品原料 / 乳底',
    brandScenario: '连锁咖啡生椰系列、新式茶饮植物基底',
    province: '海南省',
    image: '/cases/cover-coconut.png',
    desc: '文昌东郊老椰 · 1小时冷榨闭环 · 600MPa HPP锁鲜',
    poeticLine: '把海南海风里的那一口清甜，原封不动搬进咖啡杯。',
    narrative: '原产于 <span class="hl">海南省文昌</span>，经 <span class="hl">东郊椰林 → 零度生榨工厂 → HPP锁鲜中心 → -18°C冷链 → 连锁门店</span> 完成鲜椰乳供应。',
    marketInsight: '生椰已经成为年轻消费者心中“清爽、植物基、低负担”的代名词，品牌竞争焦点转向冷榨原汁和 HPP 锁鲜技术。',
    marketingCopy: '只用文昌东郊老椰，1小时生死时速生榨，600MPa超高压冷锁鲜。一口喝到现摘椰风。',
    craftBadge: 'HPP锁鲜 · 1小时生榨',
    craftTitle: '1小时的生死时速与 600MPa 冷压奇迹',
    craftSubtitle: '从老椰现采到植物基乳底',
    nodes: [
      { short: '东郊椰林', coord: [110.8783, 19.6286] },
      { short: '生榨工厂', coord: [110.7792, 19.5433] },
      { short: 'HPP中心', coord: [110.3312, 20.0311] },
      { short: '-18°C冷链', coord: [113.2644, 23.1291] },
      { short: '连锁门店', coord: [121.4737, 31.2304] }
    ],
    evidence: [
      { label: '冷榨窗口', value: '1小时' },
      { label: '锁鲜压力', value: '600MPa' },
      { label: '冷链温度', value: '-18°C' }
    ],
    craftsmanship: [
      { title: '黄金树龄老椰现采', tag: 'COCONUT', desc: '筛选树龄 15 年以上、生长期 10-12 个月的饱满老椰，锁定油脂香和月桂酸比例。' },
      { title: '1小时生榨闭环', tag: 'FRESH', desc: '采摘破壳、分离椰子水、刮取椰肉、低温冷榨，全链路在 1 小时内完成。' },
      { title: '600MPa HPP锁鲜', tag: 'HPP', desc: '用超高压冷杀菌替代高温加热，尽量保留植物蛋白和刚破壳的鲜椰香。' },
      { title: '-18°C跨海冷链', tag: 'COLD', desc: '海运与陆运串联全国中心仓，服务茶饮和咖啡门店的稳定复配需求。' }
    ]
  }
]

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
    id: 'indigo',
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
const activeThemeId = ref('nature')
const isExporting = ref(false)
const copyStatus = ref('')
const imagePosY = ref(50)
const customImage = ref(null)
const textDrafts = reactive({})

const product = computed(() => products.find(p => p.id === activeProductId.value) || products[0])
const activeTheme = computed(() => themes.find(t => t.id === activeThemeId.value) || themes[0])
const activeDraft = computed(() => {
  ensureDraft(activeProductId.value)
  return textDrafts[activeProductId.value]
})
const posterText = computed(() => activeDraft.value)
const formattedNarrative = computed(() => escapeHtml(posterText.value.narrative).replace(/\n/g, '<br>'))

function defaultDraftFor(item) {
  return {
    title: item.name,
    desc: item.desc,
    poeticLine: item.poeticLine,
    narrative: stripHtml(item.narrative),
    marketingCopy: item.marketingCopy || ''
  }
}

function ensureDraft(id) {
  if (textDrafts[id]) return
  const item = products.find(p => p.id === id) || products[0]
  textDrafts[id] = defaultDraftFor(item)
}

function resetActiveDraft() {
  textDrafts[activeProductId.value] = defaultDraftFor(product.value)
}

function handleProductChange(item) {
  activeProductId.value = item.id
  ensureDraft(item.id)
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

function stripHtml(value) {
  return value.replace(/<[^>]*>/g, '')
}

function escapeHtml(value) {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;')
}

async function writeClipboard(text) {
  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(text)
    return
  }
  const textarea = document.createElement('textarea')
  textarea.value = text
  textarea.setAttribute('readonly', '')
  textarea.style.position = 'fixed'
  textarea.style.left = '-9999px'
  document.body.appendChild(textarea)
  textarea.select()
  document.execCommand('copy')
  document.body.removeChild(textarea)
}

async function copyMarketingCopy() {
  const evidenceText = product.value.evidence.map(item => `${item.label}：${item.value}`).join('\n')
  const text = [
    `【${posterText.value.title}】`,
    posterText.value.desc,
    posterText.value.poeticLine,
    '',
    posterText.value.marketingCopy,
    '',
    `溯源叙事：${posterText.value.narrative}`,
    '',
    '核心证据：',
    evidenceText
  ].join('\n')

  try {
    await writeClipboard(text)
    copyStatus.value = '已复制'
  } catch (err) {
    console.error(err)
    copyStatus.value = '复制失败'
  } finally {
    setTimeout(() => { copyStatus.value = '' }, 1800)
  }
}

const cssVariables = computed(() => {
  const isIndigo = activeTheme.value.id === 'indigo'
  const isNature = activeTheme.value.id === 'nature'

  return {
    '--t-primary': activeTheme.value.colors.primary,
    '--t-accent': activeTheme.value.colors.accent,
    '--t-bg': activeTheme.value.colors.bg,
    '--t-paper': activeTheme.value.colors.paper,
    '--t-text': activeTheme.value.colors.text,
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
  } catch (err) {
    console.error(err)
  } finally {
    isExporting.value = false
  }
}
</script>

<style scoped>
/* ================= 工作台基础布局 (保持不变) ================= */
.marketing-studio { display: grid; grid-template-columns: 340px minmax(0, 1fr); min-height: calc(100vh - var(--navbar-h)); height: auto; margin-top: var(--navbar-h); background: #dcd9d2; }
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
.copy-editor { display: flex; flex-direction: column; gap: 10px; }
.copy-editor label { display: flex; flex-direction: column; gap: 5px; }
.copy-editor label span { font-size: 11px; color: #6e6660; font-weight: 700; }
.copy-editor input,
.copy-editor textarea {
  width: 100%;
  border: 1px solid #dfdbd2;
  border-radius: 6px;
  background: #fff;
  color: #2a2320;
  padding: 9px 10px;
  font: inherit;
  font-size: 12px;
  line-height: 1.5;
  resize: vertical;
}
.copy-editor input:focus,
.copy-editor textarea:focus {
  outline: none;
  border-color: #b85433;
  box-shadow: 0 0 0 3px rgba(184, 84, 51, 0.08);
}
.reset-copy-btn {
  padding: 9px 10px;
  border: 1px solid #d7d0c6;
  border-radius: 6px;
  background: transparent;
  color: #6e6660;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
}
.reset-copy-btn:hover { color: #b85433; border-color: #b85433; }
.export-btn { width: 100%; padding: 14px; background: #201a17; color: #faf9f6; border: none; border-radius: 6px; font-weight: 700; cursor: pointer; margin-top: auto; }
.copy-btn { width: 100%; padding: 12px; margin-top: 10px; background: #fff; color: #2a2320; border: 1px solid #d7d0c6; border-radius: 6px; font-weight: 700; cursor: pointer; }
.copy-btn:hover { border-color: #b85433; color: #b85433; background: rgba(184, 84, 51, 0.04); }
.studio-stage { min-width: 0; padding: 40px; overflow: auto; display: grid; place-items: start center; }

/* ================= 字体矩阵 ================= */
.font-modern { font-family: "PingFang SC", "Microsoft YaHei", "Helvetica Neue", -apple-system, sans-serif; }
.font-classical { font-family: "Noto Serif SC", "Songti SC", STSong, serif; }
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

.hero-image-frame { position: relative; background: var(--t-paper); overflow: hidden; }
.visual-core-img { width: 100%; height: 100%; object-fit: cover; display: block; }
.brand-title { font-weight: 700; color: var(--t-primary); margin: 0; }
.product-summary-desc { font-size: 13px; opacity: 0.8; margin: 0; line-height: 1.5; }
.poetic-bar { font-size: 12px; font-style: italic; opacity: 0.7; }
.geo-kicker { font-size: 10px; text-transform: uppercase; letter-spacing: 0.1em; opacity: 0.5; font-family: sans-serif; display: block; margin-bottom: 4px; }

.poster-section-footer { display: flex; justify-content: space-between; align-items: flex-end; margin-top: auto; padding-top: 24px; }
.footer-line { position: absolute; left: 32px; right: 32px; bottom: 85px; height: 1px; background: var(--t-primary); opacity: 0.15; }
.copyright-info strong { display: block; font-size: 12px; color: var(--t-primary); margin-bottom: 2px;}
.copyright-info span { font-size: 8px; opacity: 0.5; font-family: Arial, Helvetica, sans-serif; letter-spacing: 0.05em; }
.qr-stub { width: 36px; height: 36px; border: 1px solid var(--t-primary); opacity: 0.3; }

/* ================= 风格一：好食探索 (极简自然绿) ================= */
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

/* ================= 风格二：东方风物 (古典米色) ================= */
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

/* ================= 风格三：蓝印花布 (非遗蓝染) ================= */
.layout-indigo { position: relative; }
.layout-indigo::before {
  content: ''; position: absolute; inset: 0; z-index: 1; pointer-events: none; mix-blend-mode: overlay; opacity: 0.4;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E");
}
.layout-indigo .canvas-hairline-frame { border: 2px solid var(--t-primary); opacity: 0.8; inset: 20px; border-radius: 4px; }
.layout-indigo .poster-layout-container { padding: 48px 40px; }
.layout-indigo .hero-image-frame { width: 100%; height: 220px; border: 4px solid var(--t-primary); position: relative; }
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

@media (max-width: 1100px) {
  .marketing-studio { grid-template-columns: 300px minmax(0, 1fr); }
  .studio-sidebar { padding: 24px 18px; }
  .studio-stage { padding: 28px; }
}

@media (max-width: 860px) {
  .marketing-studio { grid-template-columns: 1fr; }
  .studio-sidebar {
    border-right: none;
    border-bottom: 1px solid rgba(0,0,0,0.08);
  }
  .studio-stage { place-items: start center; }
}

</style>
