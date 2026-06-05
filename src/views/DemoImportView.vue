<template>
  <main class="import-page">
    <AssetImport />
  </main>
</template>

<script setup>
import AssetImport from '../components/AssetImport.vue'
</script>

<style scoped>
.import-page {
  min-height: 100vh;
  padding: calc(var(--navbar-h) + 28px) var(--page-gutter) 56px;
  background: #f6f0e7;
}
</style>
