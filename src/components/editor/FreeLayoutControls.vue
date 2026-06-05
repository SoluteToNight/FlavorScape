<template>
  <div>
    <section class="field-group creative-panel">
      <div class="field-head">
        <label>画布模板</label>
        <span>{{ layout.templateName || layout.templateId || '自定义' }}</span>
      </div>
      <select class="field-input" @change="onTemplateChange">
        <option v-for="item in templateOpts" :key="item.id" :value="item.id">
          {{ item.name }} · {{ item.tone }}
        </option>
      </select>
      <div class="field-head mt-3">
        <label>尺寸</label>
        <span>{{ layout.width }}×{{ layout.height }}</span>
      </div>
      <select class="field-input" @change="onPresetChange">
        <option v-for="item in canvasPresets" :key="item.id" :value="item.id">
          {{ item.name }} · {{ item.width }}×{{ item.height }}
        </option>
      </select>
    </section>

    <section class="field-group">
      <div class="field-head">
        <label>主题</label>
        <span>{{ currentThemeName }}</span>
      </div>
      <div class="theme-grid">
        <button
          v-for="item in themeOptions"
          :key="item.id"
          type="button"
          class="theme-option"
          :class="{ active: layout.themeId === item.id }"
          @click="store.updateLayoutTheme(outputType, item.id)"
        >
          <span class="theme-swatch" :style="{ background: item.swatch }" />
          <span><strong>{{ item.name }}</strong><small>{{ item.id }}</small></span>
        </button>
      </div>
    </section>

    <ElementLibrary :add-element="addElement" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { canvasPresetOptions, inferTemplateId, templateOptions as getTemplateOptions } from '../../data/layout-presets'
import { themeOptions } from '../../data/themes'
import { useStudioStore } from '../../stores/studio'
import ElementLibrary from './ElementLibrary.vue'

const props = defineProps({
  outputType: { type: String, required: true },
})

const store = useStudioStore()

const layout = computed(() => store.activeLayout)
const canvasPresets = computed(() => canvasPresetOptions(props.outputType))
const templateOpts = computed(() => getTemplateOptions(props.outputType))
const currentThemeName = computed(() => themeOptions.find(item => item.id === layout.value?.themeId)?.name || '自定义')

function addElement(item) {
  store.addElement(props.outputType, item.type, { preset: item.preset })
}

function onTemplateChange(e) {
  if (!window.confirm('重套模板会覆盖当前画布元素。确认继续？')) return
  const template = getTemplateOptions(props.outputType).find(item => item.id === e.target.value)
  store.initLayout(props.outputType, {
    templateId: e.target.value,
    presetId: layout.value.presetId || template?.recommendedPresetId,
    themeId: layout.value.themeId || template?.recommendedThemeId,
  })
}

function onPresetChange(e) {
  if (!window.confirm('更换尺寸会按当前模板重新生成布局。确认继续？')) return
  store.initLayout(props.outputType, {
    templateId: layout.value.templateId || inferTemplateId(props.outputType, layout.value),
    presetId: e.target.value,
    themeId: layout.value.themeId,
  })
}
</script>
