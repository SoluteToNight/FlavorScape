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
        <StaticGeoMap :target-province="archiveData.province" :nodes="archiveData.spatial.nodes" />
      </div>
      <div v-if="archiveData.modules?.originInfo !== false" class="fact-card">
        <h2>产地信息</h2>
        <dl>
          <div>
            <dt>产品</dt>
            <dd>{{ archiveData.productName }}</dd>
          </div>
          <div>
            <dt>产地</dt>
            <dd>{{ archiveData.origin }}</dd>
          </div>
          <div>
            <dt>品类</dt>
            <dd>{{ archiveData.category }}</dd>
          </div>
        </dl>
      </div>
    </section>

    <section v-if="archiveData.modules?.evidenceMetrics !== false && archiveData.evidence.length" class="evidence-section">
      <h2>核心证据指标</h2>
      <div class="evidence-row">
        <div v-for="item in archiveData.evidence" :key="item.label">
          <span>{{ item.label }}</span>
          <strong>{{ item.value }}</strong>
        </div>
      </div>
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
  || props.archiveData.modules?.originInfo !== false
)
</script>

<style scoped>
.archive-canvas {
  width: 760px;
  height: 1040px;
  overflow: hidden;
  background: #fbfaf6;
  color: #201b16;
  padding: 44px;
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
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  gap: 18px;
  margin-top: 26px;
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

.map-card {
  height: 250px;
}

.map-card > div {
  height: 195px;
  margin-top: 10px;
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
}

.evidence-section,
.node-section,
footer {
  margin-top: 18px;
}

.evidence-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-top: 14px;
}

.evidence-row div,
.node-list div {
  border-top: 1px solid rgba(32,27,22,0.1);
  padding-top: 12px;
}

.evidence-row span,
.node-list span {
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

.node-list p,
footer p {
  margin-top: 8px;
  color: #5c5147;
  font-size: 12px;
  line-height: 1.7;
}

footer {
  display: grid;
  grid-template-columns: 80px 1fr;
  gap: 18px;
}
</style>
