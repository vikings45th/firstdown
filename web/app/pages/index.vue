<script setup lang="ts">
type ChatMessage = {
  id: string;
  role: "assistant" | "user" | "system";
  parts: { type: string; text: string }[];
};

interface SuggestedRoute {
  message: string;
  theme: string;
  distance_km: number;
}

const geminiStatus = ref("ready");
const isModalOpen = ref(false);

const messages = ref<ChatMessage[]>([]);
const suggestedRoute = ref<SuggestedRoute>({
  message: "頭を休ませる30分の散歩に出かける？",
  theme: "think",
  distance_km: 2,
});
const features = ref([
  {
    title: "どこを歩くか考えなくていい",
    icon: "i-lucide-route",
  },
  {
    title: "今の気分に合った散歩ができる",
    icon: "i-lucide-heart",
  },
  {
    title: "いつもと少し違う道を歩けることがある",
    icon: "i-lucide-compass",
  },
]);

const chatButtonLabels = ref(["案内してもらう", "ちょっと違う気分"]);

const firstSuggest = async () => {
  messages.value = [
    {
      id: "6045235a-a435-46b8-989d-2df38ca2eb47",
      role: "assistant",
      parts: [
        {
          type: "text",
          text: "今に合う道を探しています。",
        },
      ],
    },
  ];
  geminiStatus.value = "submitted";
  const route = await $fetch<SuggestedRoute>("/api/gemini", {
    method: "POST",
    body: {
      model: "gemini-2.5-flash",
    },
  });

  geminiStatus.value = "ready";

  suggestedRoute.value = route;

  messages.value.push({
    id: "6045235a-a435-46b8-989d-2df38ca2eb47",
    role: "assistant",
    parts: [
      {
        type: "text",
        text: route.message,
      },
    ],
  });
};

const resuggest = async () => {
  messages.value.push({
    id: "6045235a-a435-46b8-989d-2df38ca2eb47",
    role: "assistant",
    parts: [
      {
        type: "text",
        text: "別の道を探しています。",
      },
    ],
  });
  geminiStatus.value = "submitted";
  const route = await $fetch<SuggestedRoute>("/api/gemini", {
    method: "POST",
    body: {
      prevTheme: suggestedRoute.value.theme,
      prevDistance: suggestedRoute.value.distance_km,
      model: "gemini-2.5-flash",
    },
  });

  geminiStatus.value = "ready";

  suggestedRoute.value = route;

  messages.value.push({
    id: "6045235a-a435-46b8-989d-2df38ca2eb47",
    role: "assistant",
    parts: [
      {
        type: "text",
        text: route.message,
      },
    ],
  });
};

const handleButtonClick = async (label: string) => {
  messages.value.push({
    id: "6045235a-a435-46b8-989d-2df38ca2eb47",
    role: "user",
    parts: [
      {
        type: "text",
        text: label,
      },
    ],
  });

  // 0.5秒待機
  await new Promise((resolve) => setTimeout(resolve, 500));

  if (label === "案内してもらう") {
    navigateTo(
      `/app/search?theme=${suggestedRoute.value.theme}&distance_km=${suggestedRoute.value.distance_km}&quicksearch=true`,
    );
  } else if (label === "ちょっと違う気分") {
    resuggest();
  }
};

// モーダルが開いたときに自動的に提案を取得
watch(isModalOpen, (newValue) => {
  if (newValue && messages.value.length === 0) {
    firstSuggest();
  }
});
</script>

<template>
  <UPageHero
    description="あなたの気分に寄り添った散歩コースを提案します。"
    orientation="horizontal"
  >
    <template #title> 歩けた<br />それだけで今日は十分 </template>
    <img
      src="/img/heroimg.jpg"
      alt="App screenshot"
      class="rounded-lg shadow-2xl ring ring-default"
    />
  </UPageHero>
  <UPageCTA title="散歩を提案してもらう">
    <UDrawer direction="bottom" handle-only>
      <UButton
        color="primary"
        label="チャットでいくつか答えるだけです。"
        icon="i-lucide-message-circle"
        size="xl"
        block
        @click="isModalOpen = true"
      />

      <template #content>
        <div class="h-[90dvh] p-4 flex flex-col min-h-0">
          <UChatPalette class="flex-1 min-h-0 flex flex-col">
            <div class="overflow-y-auto flex-1 min-h-0">
              <UChatMessages
                should-auto-scroll
                :status="geminiStatus"
                :messages="messages"
                :assistant="{
                  avatar: {
                    icon: 'i-lucide-bot',
                  },
                }"
              />
              <div
                v-if="geminiStatus === 'ready'"
                class="flex flex-wrap gap-2 m-4 justify-end"
              >
                <UButton
                  v-for="(label, index) in chatButtonLabels"
                  :key="index"
                  :label="label"
                  :color="index === 0 ? 'primary' : 'neutral'"
                  variant="outline"
                  class="rounded-full"
                  @click="handleButtonClick(label)"
                />
              </div>
            </div>
          </UChatPalette>
        </div>
      </template>
    </UDrawer>
  </UPageCTA>
  <UPageSection
    title="散歩した方がいいと分かっている。でも疲れているとどこを歩くかを考えられない。"
    description="今の気分に沿った散歩ルートを一つだけ提案します。"
    :features="features"
  />

  <!-- モーダル -->
</template>
