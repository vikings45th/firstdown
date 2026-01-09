<script setup lang="ts">
interface Route {
  mood?: string;
  title?: string;
  polyline?: Array<{ lat: number; lng: number }>;
  summary?: string;
  distance_km?: number;
  steps?: number;
  duration_min?: number;
  spots?: string[];
}

const props = defineProps<{
  route: Route | null;
  isOpen?: boolean;
}>();

let mapInstance: any = null;
let flightPath: any = null;

function destroyMap() {
  if (flightPath) {
    flightPath.setMap(null);
    flightPath = null;
  }
  
  if (mapInstance) {
    // マップ上のすべてのオーバーレイを削除
    if (mapInstance.overlayMapTypes) {
      mapInstance.overlayMapTypes.clear();
    }
    // マップインスタンスをnullに設定
    mapInstance = null;
  }
  
  // DOM要素の内容をクリア
  const mapElement = document.getElementById("route-map");
  if (mapElement) {
    mapElement.innerHTML = '';
  }
}

function initMap() {
  const mapElement = document.getElementById("route-map");
  if (!mapElement || !(window as any).google) {
    return;
  }

  // 既にマップが初期化されている場合は削除
  if (mapInstance) {
    destroyMap();
  }
  
  // DOM要素をクリア（既存のマップ要素を削除）
  mapElement.innerHTML = '';

  // ルートの座標を取得（デフォルト値は空配列）
  const coordinates = props.route?.polyline || [];

  // まずはデフォルトの中心・ズームでマップを作る
  let center = { lat: 0, lng: -180 };
  let zoom = 2;

  mapInstance = new (window as any).google.maps.Map(mapElement, {
    zoom,
    center,
    mapTypeId: 'terrain',
  });

  // ここから polyline がある場合だけ bounds を使って再調整
  if (coordinates.length > 0 && mapInstance) {
    const bounds = new (window as any).google.maps.LatLngBounds();

    coordinates.forEach((p: { lat: number; lng: number }) => {
      bounds.extend(new (window as any).google.maps.LatLng(p.lat, p.lng));
    });

    mapInstance.fitBounds(bounds);
  }

  if (coordinates.length > 0) {
    // 既存のflightPathがあれば削除
    if (flightPath) {
      flightPath.setMap(null);
    }
    
    flightPath = new (window as any).google.maps.Polyline({
      path: coordinates,
      geodesic: true,
      strokeColor: "#FF0000",
      strokeOpacity: 1.0,
      strokeWeight: 2,
    });
    flightPath.setMap(mapInstance);
  }
}

// routeが変更された時にマップを初期化
watch(() => props.route, (newRoute) => {
  if (newRoute) {
    nextTick(() => {
      // Google Maps APIが読み込まれるまで待つ
      const checkGoogleMaps = setInterval(() => {
        if (typeof window !== 'undefined' && (window as any).google) {
          clearInterval(checkGoogleMaps);
          initMap();
        }
      }, 100);

      // タイムアウト（5秒後）
      setTimeout(() => {
        clearInterval(checkGoogleMaps);
      }, 5000);
    });
  }
}, { immediate: true });

// モーダルが閉じられた時にマップを破棄
watch(() => props.isOpen, (isOpen) => {
  if (isOpen === false) {
    destroyMap();
  }
});

// コンポーネントがアンマウントされる時にもマップを破棄
onBeforeUnmount(() => {
  destroyMap();
});
</script>

<template>
  <div v-if="route">
    <div id="route-map" style="width: 100%; height: 400px;"></div>
    <p>{{ route.summary }}</p>
    <p>{{ route.distance_km }}km、{{ route.steps }}歩、{{ route.duration_min }}分</p>
    <p>見どころスポット</p>
    <ul>
      <li v-for="spot in route.spots" :key="spot">{{ spot }}</li>
    </ul>
  </div>
</template>
