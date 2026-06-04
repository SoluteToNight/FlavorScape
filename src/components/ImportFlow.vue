<template>
  <div class="flex flex-col items-center justify-center h-full gap-6">
    <div class="glass-panel w-[420px] p-8 text-center">
      <h2 class="font-serif text-xl text-earth mb-6">正在生成空间资产</h2>
      <div class="flex flex-col gap-4">
        <div
          v-for="(step, i) in steps"
          :key="i"
          class="flex items-center gap-3 transition-all duration-300"
          :class="currentStep >= i ? 'opacity-100' : 'opacity-30'"
        >
          <div
            class="w-3 h-3 rounded-full transition-all"
            :class="currentStep >= i ? 'bg-earth scale-110' : 'bg-text-muted'"
          />
          <span
            class="text-sm"
            :class="currentStep >= i ? 'text-text font-medium' : 'text-text-muted'"
          >
            {{ step.text }}
          </span>
        </div>
      </div>
      <button class="mt-6 text-xs text-text-muted underline cursor-pointer" @click="skip">
        跳过
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  productName: { type: String, required: true },
  province: { type: String, required: true },
  nodeCount: { type: Number, required: true },
})

const emit = defineEmits(['complete'])

const currentStep = ref(-1)
const steps = ref([])
let timer = null

onMounted(() => {
  steps.value = [
    { text: `正在识别产品名称 \u2014 ${props.productName}` },
    { text: `正在提取产地信息 \u2014 ${props.province}` },
    { text: `正在匹配地理节点 \u2014 ${props.nodeCount} 个节点` },
    { text: '正在生成空间资产' },
  ]
  animateSteps()
})

onUnmounted(() => clearTimeout(timer))

function animateSteps() {
  const next = currentStep.value + 1
  if (next >= steps.value.length) {
    setTimeout(() => emit('complete'), 300)
    return
  }
  currentStep.value = next
  timer = setTimeout(animateSteps, 800)
}

function skip() {
  clearTimeout(timer)
  emit('complete')
}
</script>
