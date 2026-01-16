<script setup lang="ts">
const props = defineProps<{
  detailed: boolean;
  theme? : string;
  distance? : number;
}>();

interface LatLng {
  lat: number;
  lng: number;
}

interface ApiRequest {
  request_id: string;
  theme: string;
  distance_km: number;
  start_location: LatLng;
  end_location: LatLng;
  round_trip: boolean;
  debug: boolean;
}

interface ApiResponse {
  statusCode: number;
  body: {
    request_id: string;
    route: Route;
    meta: any;
  };
}

// ルート情報の型
interface Route {
  route_id: string;
  polyline: LatLng[];
  distance_km: number;
  duration_min: number;
  title: string;
  summary: string;
  nav_waypoints: LatLng[];
  spots: { name?: string; type?: string }[];
}

const route = ref<Route | null>(null);
const open = ref(false)
const themeItems = ref(['exercise', 'think', 'refresh', 'nature']);
const theme = ref(props.theme ?? 'exercise');
const distance = ref(Number(props.distance ?? 5));
const currentLat = ref<number>(35.685175);
const currentLng = ref<number>(139.752799);
const startLat = ref<number>(35.685175);
const startLng = ref<number>(139.752799);
const endLat = ref<number>(35.685175);
const endLng = ref<number>(139.752799)
const locationError = ref<string | null>(null);

const loadingApi = ref(false)
const loadingLocation = ref(false);

const accordionItems = [
{ label: "開始地点", key: "start" },
{ label: "終了地点", key: "end" },
]
  
const emit = defineEmits<{
  submit: [theme: string, distance: number];
}>();

watch([theme, distance], ([m, d]) => {
  emit('submit', m, d);
});

onMounted(async() => {
  await fetchCurrentLocation();
  setCurrentLatlng();

  if(props.theme && props.distance){
    callApi();
  }
})

const setCurrentLatlng = () => {
  startLat.value = currentLat.value;
  startLng.value = currentLng.value;
  endLat.value = currentLat.value;
  endLng.value = currentLng.value;
}

const setJsonPayload = (): ApiRequest => {

  //緯度 0.001° ≒ 111m、経度 0.001° ≒ 91m
  const flag:boolean = Math.abs(startLat.value - endLat.value) < 0.001 && Math.abs(startLng.value - endLng.value) < 0.001

  return {
    request_id: crypto.randomUUID(),
    theme: theme.value,
    distance_km: distance.value,
    start_location: {
      lat: startLat.value,
      lng: startLng.value
    },
    end_location: {
      lat: endLat.value,
      lng: endLng.value
    },
    round_trip: flag,
    debug: false
  };
}

const callApi = async()=> {
  loadingApi.value = true;

  const jsonPayload:ApiRequest = setJsonPayload();

  try{
    const apiResponse = await $fetch<ApiResponse>("/api/fetch-ai", {//apiResponse={statusCode: 200,body: response}
      method: "post",
      body: jsonPayload,
    });

    route.value = apiResponse.body.route;

    loadingApi.value = false;
    open.value = true;

  }catch(e){
    loadingApi.value = false;
    console.log(e);
  }
}

const fetchCurrentLocation = (): Promise<void> => {
  if (!navigator.geolocation) {
    locationError.value = 'このブラウザは位置情報取得に対応していません。';
    return Promise.resolve();
  }

  loadingLocation.value = true;
  locationError.value = null;

  return new Promise((resolve) => {
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        currentLat.value = pos.coords.latitude;
        currentLng.value = pos.coords.longitude;
        loadingLocation.value = false;
        resolve();
      },
      (err) => {
        loadingLocation.value = false;
        locationError.value = '位置情報の取得に失敗しました: ' + err.message;
        resolve(); // エラー時も完了扱いにする
      },
      {
        enableHighAccuracy: true,
        timeout: 100000,
      }
    );
  });
};

const regenerate = async() =>{
  route.value = null;
  await callApi();
  open.value = false;
}

const startNavigation = () => {
  // route が無い / polyline が空なら何もしない
  if (!route.value || !route.value.nav_waypoints || route.value.nav_waypoints.length < 2){
    return;
  }else{
    const points = route.value.nav_waypoints;
    const origin = points[0]!;
    const destination = points[points.length - 1]!;
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
  <div class="route-form space-y-6">
    <div class="space-y-2">
      <p class="text-sm font-semibold text-gray-700 tracking-wide">どんな気分？</p>
      <p class="text-xs text-gray-500">いまの気分に一番近いものを選んでください。</p>
    </div>
    <URadioGroup 
      indicator="hidden" 
      v-model="theme" 
      :items="themeItems" 
      variant="card" 
      class="mb-2"
      :ui="{
        fieldset: 'grid grid-cols-2 gap-2'
      }"
    />
    <div class="flex items-start justify-between mb-2 gap-4">
      <div class="space-y-1">
        <p class="text-sm font-semibold text-gray-700 tracking-wide">どれくらい歩く？</p>
        <p class="text-xs text-gray-500">距離を変えると、所要時間や歩数も変わります。</p>
      </div>
      <div class="text-right text-xs">
        <p class="font-semibold text-primary-600">
          {{ distance }}km
        </p>
        <p class="text-gray-500">
          約 {{ Math.round(distance/0.06) }} 分
        </p>
        <p class="text-gray-400">
          約 {{ distance*1000 }} 歩
        </p>
      </div>
    </div>
    <USlider 
      v-model="distance" 
      :min="0.5" 
      :max="10" 
      :step="0.5" 
      :default-value="5" 
      class="mb-2"
    />
    <div v-if="props.detailed">
      <div class="space-y-2 mb-2">
        <p class="text-sm font-semibold text-gray-700 tracking-wide">どこからどこまで？</p>
        <p class="text-xs text-gray-500">現在地をもとに開始地点と終了地点を指定します。</p>
      </div>
      <UButton
          size="xs"
          color="primary"
          :loading="loadingLocation"
          @click="fetchCurrentLocation"
      >
        現在地を取得
      </UButton>
      <UAccordion v-if="!loadingLocation" type="multiple" :items="accordionItems">
        <template #content="{ item }">
          <div class="space-y-3 pb-4">
            <!-- 開始地点 -->
            <template v-if="item.key === 'start'">
              <UInput
                v-model.number="startLat"
                type="number"
                step="0.000001"
                placeholder="開始地点の緯度"
              />
              <UInput
                v-model.number="startLng"
                type="number"
                step="0.000001"
                placeholder="開始地点の経度"
              />
            </template>
            <!-- 終了地点 -->
            <template v-else-if="item.key === 'end'">
              <UInput
                v-model.number="endLat"
                type="number"
                step="0.000001"
                placeholder="終了地点の緯度"
              />
              <UInput
                v-model.number="endLng"
                type="number"
                step="0.000001"
                placeholder="終了地点の経度"
              />
            </template>
          </div>
        </template>
      </UAccordion>
      <UButton 
        color="secondary"
        label="ルートを生成" 
        :loading="loadingApi"
        class="w-full mt-2"
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
    v-model:open="open" fullscreen :transition="true" :title="route?.title" v-if="route">
    <template #body>
      <RouteDetailModal :route="route" :is-open="open" />
    </template>
    <template #footer>
      <UButton label="もう一度提案求む" color="neutral" variant="outline" @click="regenerate" />
      <UButton label="これでいく！" color="secondary" @click="startNavigation"/>
    </template>
  </UModal>
</template>