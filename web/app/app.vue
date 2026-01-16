<script setup lang="ts">
  const runtimeConfig = useRuntimeConfig()
  // Google Maps APIをアプリ全体で一度だけ読み込む
  useHead({
    script: [
      {
        src: `https://maps.googleapis.com/maps/api/js?key=${runtimeConfig.public.googleMapsApiKey}&v=weekly`,
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
