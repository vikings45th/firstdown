<script setup lang="ts">
  const props = defineProps<{
    detailed: boolean;
    mood? : string;
    distance? : number;
  }>();

  const route = ref();
  const open = ref(false)
  const moodItems = ref(['exercise', 'thinking', 'reflesh', 'nature']);
  const mood = ref(props.mood ?? 'exercise');
  const distance = ref(Number(props.distance ?? 5));

  const emit = defineEmits<{
    submit: [mood: string, distance: number];
  }>();

  watch([mood, distance], ([m, d]) => {
    emit('submit', m, d);
  });

  onMounted(() => {
    if(props.mood && props.distance){
      callApi();
    }
  })

  const callApi = async()=> {
    try{
      const apiResponse = await $fetch("/api/fetch-ai", {//apiResponse={statusCode: 200,body: dummyRouteRes}
        method: "post",
        body: {mood: mood.value, distance: distance.value},
      });
      route.value = apiResponse.body;
      /*
        const dummyRouteRes = {
          mood : `${requestBody.mood}な気分`,
          title : "静寂のリバーサイドウォーク",
          polyline : [
            { lat: 37.772, lng: -122.214 },
            { lat: 21.291, lng: -157.821 },
            { lat: -18.142, lng: 178.431 },
            { lat: -27.467, lng: 153.027 },
          ],
          distance_km : requestBody.distance,
          duration_min : Math.round(requestBody.distance/0.06),
          steps : requestBody.distance*1000,
          summary : "信号の少ない川沿いの一本道。一定のリズムで歩くことで、頭の中を整理することができます。",
          spots : ["水面に映る夕日","長く続く遊歩道","静かな橋の下"]
        }
       */
      open.value = true;

    }catch(e){
      console.log(e);
    }
  }

  const regenerate = async() =>{
    open.value = false;
    route.value = null;
    await callApi();
  }

  const startNavigation = () => {
    // route が無い / polyline が空なら何もしない
    if (!route.value || !route.value.polyline || route.value.polyline.length < 2){
      return
    }else{
      const points = route.value.polyline
      const origin = points[0]
      const destination = points[points.length - 1]
      const waypoints = points
        .slice(1, -1)
        .map((p: { lat: number; lng: number }) => `${p.lat},${p.lng}`)
        .join('|')

      const params = new URLSearchParams({
        api: '1',
        origin: `${origin.lat},${origin.lng}`,
        destination: `${destination.lat},${destination.lng}`,
        travelmode: 'walking', // 徒歩ナビにする
      })

      if (waypoints) {
        params.set('waypoints', waypoints)
      }

      const url = `https://www.google.com/maps/dir/?${params.toString()}`
      window.open(url, '_blank') // 同タブなら '_self'
    }
  }
</script>
  
<template>
  <div>
    <p class="mb-4">気分を選ぶ</p>
    <URadioGroup 
      indicator="hidden" 
      v-model="mood" 
      :items="moodItems" 
      variant="card" 
      class="mb-4"
      :ui="{
        fieldset: 'grid grid-cols-2 gap-2'
      }"
    />
    <div class="flex justify-between mb-4">
      <p>距離を選ぶ</p>
      <p>{{ distance }}km、{{ Math.round(distance/0.06) }}分、{{ distance*1000 }}歩</p>
    </div>
    <USlider 
      v-model="distance" 
      :min="0" 
      :max="10" 
      :step="0.5" 
      :default-value="5" 
      class="mb-4"
    />
    <div v-if="props.detailed">
      <p>出発・終了地点を選ぶ</p>
      <p>[input field][input field]</p>
      <p>より細かい要望を記入</p>
      <p>[input field]</p>
      <UButton 
        color="primary" 
        label="ルートを生成" 
        @click="callApi"
      />
    </div>
  </div>
  <UModal
    :close="{
      label: '条件を変更',
      color: 'primary',
      variant: 'outline',
      class: 'rounded-full'
    }"
    v-model:open="open" fullscreen :transition="true" :title="route?.title" :description="route?.mood" v-if="route">
    <template #body>
      <RouteDetailModal :route="route" :is-open="open" />
    </template>
    <template #footer>
      <UButton label="もう一度提案求む" color="neutral" variant="outline" @click="regenerate" />
      <UButton label="これでいく！" color="secondary" @click="startNavigation"/>
    </template>
  </UModal>
</template>