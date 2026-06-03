<template>
  <div class="flex flex-col items-center justify-center h-full gap-8 p-8">
    <div class="text-center">
      <h2 class="font-serif text-3xl text-earth mb-2">选择产品，开始创作</h2>
      <p class="text-sm text-text-mid">你的第一个品牌空间资产</p>
    </div>
    <div class="flex gap-4 flex-wrap justify-center">
      <button
        v-for="pc in productCases"
        :key="pc.id"
        class="glass-panel w-[180px] p-4 text-left cursor-pointer transition-all duration-250 hover:-translate-y-1 hover:shadow-app-md"
        @click="$emit('select', pc.id)"
      >
        <div class="w-full h-[100px] bg-bg-warm rounded mb-3 flex items-center justify-center text-3xl">
          {{ pc.name.slice(0, 2) }}
        </div>
        <div class="font-serif text-base text-text">{{ pc.name }}</div>
        <div class="text-xs text-text-muted mt-1">{{ pc.category }}</div>
      </button>
    </div>
    <button class="text-xs text-text-muted underline cursor-pointer mt-2" @click="onImportClick">
      或点击导入已有品牌资料 &rarr;
    </button>
  </div>
</template>

<script setup>
import { useProductCases } from '../composables/useProductCases'

defineEmits(['select'])
const { cases, loadAll } = useProductCases()
loadAll()
const productCases = cases

function onImportClick() {
  alert('此功能即将上线，当前为演示模式')
}
</script>
