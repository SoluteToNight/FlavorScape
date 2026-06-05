<template>
  <section class="property-inspector">
    <header class="editor-panel-head">
      <span>Inspector</span>
      <strong>{{ element ? labelForElementType(element.type) : '属性' }}</strong>
    </header>

    <div v-if="!element" class="empty-property">
      从画布或图层面板选择元素后，在这里编辑位置、样式和内容。
    </div>

    <div v-else class="property-scroll">
      <section class="prop-section">
        <div class="prop-section-title">基础</div>
        <div class="prop-grid">
          <label><span>X</span><input type="number" :value="element.x" @input="patchNumber('x', $event)" /></label>
          <label><span>Y</span><input type="number" :value="element.y" @input="patchNumber('y', $event)" /></label>
          <label><span>W</span><input type="number" :value="element.w" @input="patchSize('w', $event)" /></label>
          <label><span>H</span><input type="number" :value="element.h" @input="patchSize('h', $event)" /></label>
          <label><span>透明度</span><input type="number" min="0" max="1" step="0.05" :value="element.opacity ?? 1" @input="patchNumber('opacity', $event)" /></label>
          <label><span>层级</span><input type="number" :value="element.zIndex || 1" @input="patchNumber('zIndex', $event)" /></label>
        </div>
        <div class="check-row-group">
          <label><input type="checkbox" :checked="element.visible !== false" @change="patch({ visible: $event.target.checked })" />显示</label>
          <label><input type="checkbox" :checked="element.locked" @change="patch({ locked: $event.target.checked })" />锁定</label>
        </div>
      </section>

      <section v-if="['text', 'richText'].includes(element.type)" class="prop-section">
        <div class="prop-section-title">文本</div>
        <textarea :value="element.content" rows="5" @input="patch({ content: $event.target.value })" />
        <div class="prop-grid">
          <label><span>字号</span><input type="number" :value="element.fontSize" @input="patchNumber('fontSize', $event)" /></label>
          <label><span>行高</span><input type="number" step="0.1" :value="element.lineHeight" @input="patchNumber('lineHeight', $event)" /></label>
          <label><span>字重</span><input type="number" step="100" :value="element.fontWeight || 400" @input="patchNumber('fontWeight', $event)" /></label>
          <label><span>颜色</span><input type="color" :value="element.color || '#201b16'" @input="patch({ color: $event.target.value })" /></label>
        </div>
        <div class="segmented">
          <button v-for="value in ['left', 'center', 'right']" :key="value" type="button" :class="{ active: element.textAlign === value }" @click="patch({ textAlign: value })">{{ value }}</button>
        </div>
      </section>

      <section v-if="element.type === 'image'" class="prop-section">
        <div class="prop-section-title">图片</div>
        <button type="button" class="wide-btn" @click="$emit('upload-image', element.id)">{{ element.src ? '替换图片' : '上传图片' }}</button>
        <label><span>填充方式</span><select :value="element.objectFit || 'cover'" @change="patch({ objectFit: $event.target.value })"><option>cover</option><option>contain</option><option>fill</option></select></label>
        <div class="prop-grid">
          <label><span>焦点 X</span><input type="number" :value="element.objectPositionX ?? 50" @input="patchNumber('objectPositionX', $event)" /></label>
          <label><span>焦点 Y</span><input type="number" :value="element.objectPositionY ?? 50" @input="patchNumber('objectPositionY', $event)" /></label>
          <label><span>圆角</span><input type="number" :value="element.borderRadius || 0" @input="patchNumber('borderRadius', $event)" /></label>
        </div>
      </section>

      <section v-if="['badge', 'labelPill'].includes(element.type)" class="prop-section">
        <div class="prop-section-title">标签</div>
        <input :value="element.content" @input="patch({ content: $event.target.value })" />
        <div class="prop-grid">
          <label><span>文字</span><input type="color" :value="element.color || '#201b16'" @input="patch({ color: $event.target.value })" /></label>
          <label><span>背景</span><input type="color" :value="safeColor(element.bgColor)" @input="patch({ bgColor: $event.target.value })" /></label>
          <label><span>圆角</span><input type="number" :value="element.borderRadius || 999" @input="patchNumber('borderRadius', $event)" /></label>
        </div>
      </section>

      <section v-if="element.type === 'icon'" class="prop-section">
        <div class="prop-section-title">图标</div>
        <label><span>图标</span><select :value="element.iconName || 'MapPin'" @change="patch({ iconName: $event.target.value })"><option v-for="item in ICON_OPTIONS" :key="item.name" :value="item.name">{{ item.label }} · {{ item.name }}</option></select></label>
        <div class="prop-grid">
          <label><span>颜色</span><input type="color" :value="element.color || '#201b16'" @input="patch({ color: $event.target.value })" /></label>
          <label><span>线宽</span><input type="number" step="0.25" :value="element.strokeWidth || 1.8" @input="patchNumber('strokeWidth', $event)" /></label>
        </div>
      </section>

      <section v-if="element.type === 'metricCard'" class="prop-section">
        <div class="prop-section-title">指标卡</div>
        <input :value="element.label" placeholder="指标名称" @input="patch({ label: $event.target.value })" />
        <input :value="element.value" placeholder="指标值" @input="patch({ value: $event.target.value })" />
        <textarea :value="element.note" rows="3" placeholder="说明" @input="patch({ note: $event.target.value })" />
        <div class="prop-grid">
          <label><span>主色</span><input type="color" :value="element.valueColor || '#201b16'" @input="patch({ valueColor: $event.target.value })" /></label>
          <label><span>底色</span><input type="color" :value="safeColor(element.paper)" @input="patch({ paper: $event.target.value })" /></label>
        </div>
      </section>

      <section v-if="element.type === 'certCard'" class="prop-section">
        <div class="prop-section-title">凭证卡</div>
        <input :value="element.org" placeholder="机构" @input="patch({ org: $event.target.value })" />
        <input :value="element.result" placeholder="结果" @input="patch({ result: $event.target.value })" />
        <input :value="element.code" placeholder="编号" @input="patch({ code: $event.target.value })" />
      </section>

      <section v-if="element.type === 'timelineNode'" class="prop-section">
        <div class="prop-section-title">节点链路</div>
        <input :value="element.title" placeholder="节点标题" @input="patch({ title: $event.target.value })" />
        <textarea :value="element.desc" rows="3" placeholder="节点描述" @input="patch({ desc: $event.target.value })" />
      </section>

      <section v-if="element.type === 'chartBlock'" class="prop-section">
        <div class="prop-section-title">图表块</div>
        <label><span>类型</span><select :value="element.chartKind || 'trend'" @change="patch({ chartKind: $event.target.value })"><option value="trend">趋势</option><option value="radar">雷达</option><option value="bar">柱状</option></select></label>
        <input :value="element.title" placeholder="标题" @input="patch({ title: $event.target.value })" />
      </section>

      <section v-if="['shape', 'divider', 'lineArrow'].includes(element.type)" class="prop-section">
        <div class="prop-section-title">图形</div>
        <div class="prop-grid">
          <label><span>颜色</span><input type="color" :value="element.fill || element.color || '#201b16'" @input="patchShapeColor($event.target.value)" /></label>
          <label><span>粗细/圆角</span><input type="number" :value="element.thickness || element.borderRadius || 1" @input="patchGraphicNumber($event)" /></label>
        </div>
      </section>

      <section v-if="['mapBlock', 'mapLegend', 'evidenceBlock', 'narrativeBlock', 'quoteBlock', 'qrPlaceholder'].includes(element.type)" class="prop-section">
        <div class="prop-section-title">组件说明</div>
        <p class="property-note">该组件可调整位置、尺寸、颜色和层级；内容默认来自项目数据，也可以在模板中预置。</p>
      </section>
    </div>
  </section>
</template>

<script setup>
import { ICON_OPTIONS, labelForElementType } from '../../data/editor-elements'

const props = defineProps({
  element: { type: Object, default: null },
})

const emit = defineEmits(['update', 'upload-image'])

function patch(value) {
  emit('update', value)
}

function patchNumber(key, event) {
  patch({ [key]: Number(event.target.value) })
}

function patchSize(key, event) {
  patch({ [key]: Math.max(12, Number(event.target.value)) })
}

function patchShapeColor(value) {
  if (props.element.type === 'shape') patch({ fill: value })
  else patch({ color: value })
}

function patchGraphicNumber(event) {
  const value = Number(event.target.value)
  if (props.element.type === 'shape') patch({ borderRadius: value })
  else patch({ thickness: value })
}

function safeColor(value) {
  return value && value !== 'transparent' ? value : '#ffffff'
}
</script>

<style scoped>
.property-inspector {
  display: grid;
  min-height: 0;
  grid-template-rows: auto minmax(0, 1fr);
}

.editor-panel-head {
  display: grid;
  gap: 2px;
  padding: 12px;
  border-bottom: 1px solid rgba(74, 65, 55, 0.12);
  background: rgba(255, 252, 247, 0.58);
}

.editor-panel-head span,
.prop-section-title {
  color: var(--text-muted);
  font-size: 10px;
  font-weight: 850;
  text-transform: uppercase;
}

.editor-panel-head strong {
  color: var(--text);
  font-size: 14px;
  font-weight: 850;
}

.property-scroll {
  min-height: 0;
  overflow: auto;
  padding: 12px;
}

.prop-section {
  display: grid;
  gap: 9px;
  padding: 12px 0;
  border-bottom: 1px solid rgba(74, 65, 55, 0.1);
}

.prop-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

label {
  display: grid;
  gap: 5px;
  color: var(--text-muted);
  font-size: 10px;
  font-weight: 800;
}

input,
textarea,
select {
  width: 100%;
  border: 1px solid rgba(74, 65, 55, 0.14);
  border-radius: 5px;
  background: rgba(255, 252, 247, 0.82);
  color: var(--text);
  font-size: 12px;
  outline: none;
  padding: 8px;
}

textarea {
  resize: vertical;
}

.check-row-group {
  display: flex;
  gap: 12px;
}

.check-row-group label {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.check-row-group input {
  width: auto;
}

.segmented {
  display: inline-flex;
  width: 100%;
  gap: 2px;
  padding: 3px;
  border: 1px solid rgba(74, 65, 55, 0.13);
  border-radius: 5px;
  background: rgba(246, 243, 235, 0.76);
}

.segmented button,
.wide-btn {
  min-height: 30px;
  border: 1px solid rgba(74, 65, 55, 0.13);
  border-radius: 4px;
  background: rgba(255, 252, 247, 0.72);
  color: var(--text-mid);
  cursor: pointer;
  font-size: 11px;
  font-weight: 800;
}

.segmented button {
  flex: 1;
  border: 0;
  background: transparent;
}

.segmented button.active {
  background: rgba(139, 94, 52, 0.12);
  color: var(--earth);
}

.empty-property {
  margin: 12px;
  padding: 12px;
  border: 1px dashed rgba(74, 65, 55, 0.18);
  border-radius: 6px;
  background: rgba(255, 252, 247, 0.5);
  color: var(--text-muted);
  font-size: 12px;
  line-height: 1.65;
}

.property-note {
  margin: 0;
  color: var(--text-muted);
  font-size: 11px;
  line-height: 1.6;
}
</style>
