<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold text-gray-900">角色库</h1>
      <div class="flex gap-2">
        <button
          @click="showTemplates = true"
          :class="['px-4 py-2 rounded-md', showTemplates ? 'bg-primary-600 text-white' : 'bg-white text-gray-700 border']"
        >
          系统模板
        </button>
        <button
          @click="showTemplates = false"
          :class="['px-4 py-2 rounded-md', !showTemplates ? 'bg-primary-600 text-white' : 'bg-white text-gray-700 border']"
        >
          我的角色
        </button>
      </div>
    </div>

    <div v-if="loading" class="text-center py-8">
      <div class="spinner mx-auto"></div>
    </div>

    <div v-else-if="characters.length === 0" class="text-center py-8 text-gray-600">
      {{ showTemplates ? '暂无系统模板' : '还没有自定义角色，'
      }}<router-link v-if="!showTemplates" to="/characters/new" class="text-primary-600">创建一个</router-link>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="character in characters"
        :key="character.id"
        class="bg-white p-6 rounded-lg shadow-sm hover:shadow-md transition-shadow cursor-pointer"
        @click="goToCharacter(character.id)"
      >
        <div class="flex items-center mb-4">
          <div v-if="character.avatar_url" class="w-12 h-12 rounded-full bg-gray-200 overflow-hidden mr-4">
            <img :src="character.avatar_url" :alt="character.name" class="w-full h-full object-cover" />
          </div>
          <div v-else class="w-12 h-12 rounded-full bg-primary-100 flex items-center justify-center mr-4">
            <span class="text-primary-600 font-semibold text-xl">{{ character.name[0] }}</span>
          </div>
          <div>
            <h3 class="text-lg font-semibold text-gray-900">{{ character.name }}</h3>
            <p class="text-sm text-gray-500">
              {{ character.is_template ? '系统模板' : '自定义' }}
            </p>
          </div>
        </div>
        <div class="text-sm text-gray-600">
          <p class="mb-1">职业：{{ character.config?.profession || '未知' }}</p>
          <p>使用次数：{{ character.usage_count }}</p>
          <p>评分：{{ character.rating_avg || '暂无' }}</p>
        </div>
      </div>
    </div>

    <router-link
      v-if="!showTemplates"
      to="/characters/new"
      class="fixed bottom-8 right-8 bg-primary-600 text-white w-14 h-14 rounded-full flex items-center justify-center shadow-lg hover:bg-primary-700 transition-colors"
    >
      <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
      </svg>
    </router-link>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import endpoints from '@/services/endpoints'

const router = useRouter()
const characters = ref([])
const loading = ref(true)
const showTemplates = ref(true)

const loadCharacters = async () => {
  loading.value = true
  try {
    if (showTemplates.value) {
      const response = await endpoints.characters.getTemplates()
      characters.value = response.data
    } else {
      const response = await endpoints.characters.getMine()
      characters.value = response.data
    }
  } catch (error) {
    console.error('Failed to load characters:', error)
  } finally {
    loading.value = false
  }
}

const goToCharacter = (id) => {
  router.push(`/characters/${id}`)
}

watch(showTemplates, () => {
  loadCharacters()
})

onMounted(() => {
  loadCharacters()
})
</script>
