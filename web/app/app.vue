<script setup lang="ts">
  // Google Maps APIをアプリ全体で一度だけ読み込む
  useHead({
    script: [
      {
        src: 'https://maps.googleapis.com/maps/api/js?key=AIzaSyAFhnRF8Mg46-4tlkOEWX0_0EG3Oy59Dz4&v=weekly',
        defer: true,
        key: 'google-maps-api' // 重複を防ぐためのキー
      }
    ]
  })
</script>
  
<template>
  <UApp>
    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>
  </UApp>
</template>
