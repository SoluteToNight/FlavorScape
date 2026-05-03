<template>
  <div ref="chartEl" :style="{ width: size + 'px', height: size + 'px' }" />
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  scores: { type: Array, required: true },
  color:  { type: String, default: '#C8960F' },
  size:   { type: Number, default: 120 },
  animated: { type: Boolean, default: false },
})

const dims = ['麻', '辣', '咸', '酸', '甜', '鲜']
const chartEl = ref(null)
let chart = null

function buildOption() {
  return {
    radar: {
      center: ['50%', '50%'],
      radius: '62%',
      indicator: dims.map(d => ({ name: d, max: 1 })),
      shape: 'polygon',
      splitNumber: 4,
      axisName: {
        color: 'rgba(87,83,78,0.6)',
        fontSize: 8,
        fontFamily: "'Noto Sans SC', sans-serif",
        padding: [2, 0],
      },
      splitLine: { lineStyle: { color: 'rgba(0,0,0,0.06)' } },
      splitArea: { show: false },
      axisLine: { lineStyle: { color: 'rgba(0,0,0,0.06)' } },
    },
    series: [{
      type: 'radar',
      data: [{
        value: props.scores,
        name: '',
        areaStyle: { color: props.color + '28' },
        lineStyle: { color: props.color, width: 1.5 },
        itemStyle: { color: props.color },
        symbol: 'circle',
        symbolSize: 3,
      }],
      animation: props.animated,
      animationDuration: props.animated ? 800 : 0,
      animationEasing: 'cubicOut',
      silent: true,
    }],
  }
}

onMounted(() => {
  chart = echarts.init(chartEl.value, null, { renderer: 'canvas' })
  chart.setOption(buildOption())
})

watch(() => [props.scores, props.color], () => {
  chart?.setOption(buildOption())
}, { deep: true })

if (import.meta.hot) {
  import.meta.hot.dispose(() => chart?.dispose())
}

onUnmounted(() => {
  chart?.dispose()
})
</script>
