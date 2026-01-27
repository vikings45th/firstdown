<script setup lang="ts">
  const themeItems = ref([{
    label: '体を動かしたい',
    value: 'exercise',
  }, {
    label: '考え事をしたい',
    value: 'think',
  }, {
    label: 'リフレッシュしたい',
    value: 'refresh',
  }, {
    label: '自然を感じたい',
    value: 'nature',
  }]);
	const theme = ref("exercise");
	const colorItems = ref([
  // exercise｜体を動かしたい - 暖色・エネルギー
  {
    value: 'exercise-light',
    ui: {
      item: `bg-[#F4A896] data-[state=checked]:bg-[#F4A896]`
    }
  },
  {
    value: 'exercise-medium',
    ui: {
      item: `bg-[#E76F51] data-[state=checked]:bg-[#E76F51]`
    }
  },
  {
    value: 'exercise-heavy',
    ui: {
      item: `bg-[#C8553D] data-[state=checked]:bg-[#C8553D]`
    }
  },

  // think｜考え事をしたい - 寒色・低刺激
  {
    value: 'think-light',
    ui: {
      item: `bg-[#A8B9C9] data-[state=checked]:bg-[#A8B9C9]`
    }
  },
  {
    value: 'think-medium',
    ui: {
      item: `bg-[#5C7D99] data-[state=checked]:bg-[#5C7D99]`
    }
  },
  {
    value: 'think-heavy',
    ui: {
      item: `bg-[#3E5C73] data-[state=checked]:bg-[#3E5C73]`
    }
  },

  // refresh｜リフレッシュしたい - 中立・切り替え
  {
    value: 'refresh-light',
    ui: {
      item: `bg-[#F3E4B5] data-[state=checked]:bg-[#F3E4B5]`
    }
  },
  {
    value: 'refresh-medium',
    ui: {
      item: `bg-[#E9C46A] data-[state=checked]:bg-[#E9C46A]`
    }
  },
  {
    value: 'refresh-heavy',
    ui: {
      item: `bg-[#D4A939] data-[state=checked]:bg-[#D4A939]`
    }
  },

  // nature｜自然を感じたい - 緑・安心感
  {
    value: 'nature-light',
    ui: {
      item: `bg-[#B7D3C1] data-[state=checked]:bg-[#B7D3C1]`
    }
  },
  {
    value: 'nature-medium',
    ui: {
      item: `bg-[#6A9F7A] data-[state=checked]:bg-[#6A9F7A]`
    }
  },
  {
    value: 'nature-heavy',
    ui: {
      item: `bg-[#4F7F5E] data-[state=checked]:bg-[#4F7F5E]`
    }
  }
])

	const colorValue = ref('exercise-medium')

	const handleColorChange = (value: string) => {
		// valueからthemeを抽出（例: 'exercise-medium' → 'exercise'）
		const theme = value.split('-')[0]
		const motivation = value.split('-')[1]
		// URLにナビゲート
		navigateTo(`/app/search?theme=${theme}&motivation=${motivation}&quicksearch=true`)
	}

	const features = ref([
		{
			title: 'どこを歩くか考えなくていい',
			icon: 'i-lucide-smile',
		},
		{
			title: '今の気分に合った散歩ができる',
			icon: 'i-lucide-a-large-small',
		},
		{
			title: 'いつもと少し違う道を歩けることがある',
			icon: 'i-lucide-sun-moon',
		}
	])

	const ctaLinks = ref([
		{
			label: '散歩する',
			to: '/app/search',
			icon: 'i-lucide-square-play'
		},
	])
</script>

<template>
	<UPageHero
		title="今の気分に、ちょうどいい道。"
		description="気分に合わせて「少しだけ新しい散歩ルート」が見つかる"
		orientation="horizontal"
	>
		<img
      src="/img/heroimg.jpg"
      alt="App screenshot"
      class="rounded-lg shadow-2xl ring ring-default"
    />
	</UPageHero>
				<!--
	<UPageSection
    title="早速歩く"
		description="今どんな気分？"
  >
		<div>

      <div class="overflow-x-auto pb-4 mr-2 px-2 scrollbar-hide">
        <URadioGroup 
          indicator="hidden"
          orientation="horizontal"
          v-model="theme" 
          :items="themeItems" 
          variant="card"
          :ui="{
            wrapper: 'shrink-0 whitespace-nowrap w-auto',  
          }"
        />
      </div>
			<UButton block label="散歩ルートを検索" color="secondary" :to="`/app/search?theme=${theme}&quicksearch=true`" class="text-lg mb-2 font-bold rounded-full"/>
			<UButton block label="詳細条件を入力" color="secondary" variant="link" to="/app/search" class="rounded-full"/>
		</div>
	</UPageSection>
				-->
	<UPageSection
    title="気分に会う色を選んで歩く"
  >
        <URadioGroup 
          indicator="hidden"
          v-model="colorValue" 
          :items="colorItems" 
          variant="card"
          :ui="{
            fieldset: 'grid grid-cols-3 gap-4'
          }"
          @update:modelValue="handleColorChange"
        >
        </URadioGroup>
	</UPageSection>

	<UPageSection
    title="散歩はやったほうがいいと分かっている。でも、疲れていると「どこを歩くか」を考えられない。"
		description="このアプリは、今の気分に沿った散歩ルートを一つだけ提案します。"
		:features="features"
  />
	<UPageCTA
		title="考えなくていい。今の気分のまま、外に出られる。"
		:links="ctaLinks"
	/>
</template>

<style scoped>
	.scrollbar-hide {
		-ms-overflow-style: none;  /* IE and Edge */
		scrollbar-width: none;  /* Firefox */
	}
	
	.scrollbar-hide::-webkit-scrollbar {
		display: none;  /* Chrome, Safari and Opera */
	}
</style>