<template>
  <aside v-if="mergedData" class="overflow-y-auto border-r border-glass-border p-4">
    <div class="mb-5">
      <span class="text-2xs uppercase tracking-[0.12em] text-text-muted">创意编辑</span>
      <h2 class="font-serif text-lg text-earth mt-0.5">编辑面板</h2>
    </div>

    <!-- Desc field -->
    <div class="glass-panel p-3 mb-3">
      <div class="flex justify-between items-center mb-1.5">
        <label class="text-xs text-text-mid font-bold">产品描述</label>
        <span class="text-2xs text-text-muted">{{ descLength }}/60</span>
      </div>
      <input
        v-model="localDesc"
        type="text"
        maxlength="60"
        class="w-full bg-bg border border-glass-border rounded-sm px-3 py-1.5 text-sm text-text outline-none focus:border-earth transition-colors"
        @input="onFieldChange('desc', $event)"
      />
      <button
        class="text-2xs text-text-muted underline mt-1.5 cursor-pointer hover:text-earth transition-colors"
        @click="resetField('desc')"
      >
        重置
      </button>
    </div>

    <!-- PoeticLine field -->
    <div class="glass-panel p-3 mb-3">
      <div class="flex justify-between items-center mb-1.5">
        <label class="text-xs text-text-mid font-bold">诗意短句</label>
        <span class="text-2xs text-text-muted">{{ poeticLength }}/40</span>
      </div>
      <input
        v-model="localPoeticLine"
        type="text"
        maxlength="40"
        class="w-full bg-bg border border-glass-border rounded-sm px-3 py-1.5 text-sm text-text outline-none focus:border-earth transition-colors"
        @input="onFieldChange('poeticLine', $event)"
      />
      <button
        class="text-2xs text-text-muted underline mt-1.5 cursor-pointer hover:text-earth transition-colors"
        @click="resetField('poeticLine')"
      >
        重置
      </button>
    </div>

    <!-- Narrative field -->
    <div class="glass-panel p-3 mb-3">
      <div class="flex justify-between items-center mb-1.5">
        <label class="text-xs text-text-mid font-bold">品牌叙事</label>
        <span class="text-2xs text-text-muted">{{ narrativeLength }}/300</span>
      </div>
      <textarea
        v-model="localNarrative"
        maxlength="300"
        rows="5"
        class="w-full bg-bg border border-glass-border rounded-sm px-3 py-1.5 text-sm text-text outline-none focus:border-earth transition-colors resize-y"
        @input="onFieldChange('narrative', $event)"
      />
      <button
        class="text-2xs text-text-muted underline mt-1.5 cursor-pointer hover:text-earth transition-colors"
        @click="resetField('narrative')"
      >
        重置
      </button>
    </div>

    <!-- Theme field -->
    <div class="glass-panel p-3 mb-3">
      <div class="flex justify-between items-center mb-1.5">
        <label class="text-xs text-text-mid font-bold">视觉主题</label>
      </div>
      <select
        v-model="localTheme"
        class="w-full bg-bg border border-glass-border rounded-sm px-3 py-1.5 text-sm text-text outline-none focus:border-earth transition-colors cursor-pointer"
        @change="onFieldChange('theme', $event)"
      >
        <option value="nature">自然系 — nature</option>
        <option value="heritage">传承系 — heritage</option>
        <option value="indigo">靛蓝系 — indigo</option>
      </select>
      <button
        class="text-2xs text-text-muted underline mt-1.5 cursor-pointer hover:text-earth transition-colors"
        @click="resetField('theme')"
      >
        重置
      </button>
    </div>
  </aside>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useStudioStore } from '../stores/studio'

const store = useStudioStore()
const mergedData = computed(() => store.mergedMarketingData)

// Local reactive copies so v-model works smoothly
const localDesc = ref('')
const localPoeticLine = ref('')
const localNarrative = ref('')
const localTheme = ref('nature')

// Sync local refs whenever mergedData changes (project switch or reset)
watch(
  () => mergedData.value?.creative,
  (creative) => {
    if (creative) {
      localDesc.value = creative.desc || ''
      localPoeticLine.value = creative.poeticLine || ''
      localNarrative.value = creative.narrative || ''
      localTheme.value = creative.theme || 'nature'
    } else {
      localDesc.value = ''
      localPoeticLine.value = ''
      localNarrative.value = ''
      localTheme.value = 'nature'
    }
  },
  { immediate: true }
)

// Character counts
const descLength = computed(() => localDesc.value.length)
const poeticLength = computed(() => localPoeticLine.value.length)
const narrativeLength = computed(() => localNarrative.value.length)

function onFieldChange(field, event) {
  store.updateCreative('marketing', field, event.target.value)
}

function resetField(field) {
  store.resetToDefault('marketing', field)
}
</script>
