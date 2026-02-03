<template>
  <div>
    <div v-if="loading" class="text-center py-8">
      <div class="spinner mx-auto"></div>
    </div>

    <div v-else-if="!character" class="text-center py-8 text-gray-600">
      角色不存在
    </div>

    <div v-else class="max-w-2xl">
      <div class="bg-white p-6 rounded-lg shadow-sm mb-6">
        <div class="flex items-start mb-6">
          <div v-if="character.avatar_url" class="w-20 h-20 rounded-full bg-gray-200 overflow-hidden mr-6">
            <img :src="character.avatar_url" :alt="character.name" class="w-full h-full object-cover" />
          </div>
          <div v-else class="w-20 h-20 rounded-full bg-primary-100 flex items-center justify-center mr-6">
            <span class="text-primary-600 font-bold text-3xl">{{ character.name[0] }}</span>
          </div>
          <div class="flex-1">
            <h1 class="text-3xl font-bold text-gray-900 mb-2">{{ character.name }}</h1>
            <p class="text-gray-600">
              {{ character.config?.profession || '未知职业' }}
              <span v-if="character.is_template" class="ml-2 text-sm text-primary-600">
                （系统模板）
              </span>
            </p>
          </div>
        </div>

        <div v-if="character.config" class="space-y-4">
          <div>
            <h3 class="font-medium text-gray-900 mb-2">基本信息</h3>
            <div class="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span class="text-gray-500">年龄：</span>
                <span>{{ character.config.age || '未知' }}</span>
              </div>
              <div>
                <span class="text-gray-500">性别：</span>
                <span>{{ character.config.gender || '未知' }}</span>
              </div>
            </div>
          </div>

          <div>
            <h3 class="font-medium text-gray-900 mb-2">性格特质</h3>
            <div v-if="character.config.personality" class="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span class="text-gray-500">开放性：</span>
                <span>{{ character.config.personality.openness }}/10</span>
              </div>
              <div>
                <span class="text-gray-500">严谨性：</span>
                <span>{{ character.config.personality.rigor }}/10</span>
              </div>
              <div>
                <span class="text-gray-500">批判性思维：</span>
                <span>{{ character.config.personality.critical_thinking }}/10</span>
              </div>
              <div>
                <span class="text-gray-500">乐观程度：</span>
                <span>{{ character.config.personality.optimism }}/10</span>
              </div>
            </div>
          </div>

          <div>
            <h3 class="font-medium text-gray-900 mb-2">知识背景</h3>
            <div v-if="character.config.knowledge" class="text-sm space-y-2">
              <div>
                <span class="text-gray-500">专业领域：</span>
                <span>{{ character.config.knowledge.fields?.join('、') || '无' }}</span>
              </div>
              <div>
                <span class="text-gray-500">经验年限：</span>
                <span>{{ character.config.knowledge.experience_years || 0 }} 年</span>
              </div>
              <div v-if="character.config.knowledge.representative_views && character.config.knowledge.representative_views.length > 0">
                <span class="text-gray-500">代表观点：</span>
                <span>{{ character.config.knowledge.representative_views.join('、') }}</span>
              </div>
            </div>
          </div>

          <div>
            <h3 class="font-medium text-gray-900 mb-2">讨论风格</h3>
            <div class="text-sm space-y-2">
              <div>
                <span class="text-gray-500">立场：</span>
                <span>{{ getStanceText(character.config.stance) }}</span>
              </div>
              <div>
                <span class="text-gray-500">表达风格：</span>
                <span>{{ getExpressionStyleText(character.config.expression_style) }}</span>
              </div>
              <div>
                <span class="text-gray-500">行为模式：</span>
                <span>{{ getBehaviorPatternText(character.config.behavior_pattern) }}</span>
              </div>
            </div>
          </div>

          <div class="grid grid-cols-3 gap-4 pt-4 border-t">
            <div class="text-center">
              <div class="text-2xl font-bold text-primary-600">{{ character.usage_count }}</div>
              <div class="text-sm text-gray-500">使用次数</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-primary-600">{{ character.rating_avg }}</div>
              <div class="text-sm text-gray-500">平均评分</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-primary-600">{{ character.rating_count }}</div>
              <div class="text-sm text-gray-500">评分人数</div>
            </div>
          </div>
        </div>
      </div>

      <div class="flex gap-4">
        <router-link
          :to="`/discussions/new?character=${character.id}`"
          class="flex-1 bg-primary-600 text-white px-6 py-2 rounded-md hover:bg-primary-700 text-center"
        >
          使用此角色
        </router-link>
        <router-link
          to="/characters"
          class="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
        >
          返回列表
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import endpoints from '@/services/endpoints'

const route = useRoute()
const router = useRouter()
const characterId = route.params.id

const character = ref(null)
const loading = ref(true)

const loadCharacter = async () => {
  try {
    const response = await endpoints.characters.getById(characterId)
    character.value = response.data
  } catch (error) {
    console.error('Failed to load character:', error)
  } finally {
    loading.value = false
  }
}

const getStanceText = (stance) => {
  const texts = {
    support: '支持',
    oppose: '反对',
    neutral: '中立',
    critical_exploration: '批判性探索'
  }
  return texts[stance] || stance
}

const getExpressionStyleText = (style) => {
  const texts = {
    formal: '正式',
    casual: '随意',
    technical: '技术性',
    storytelling: '叙事性'
  }
  return texts[style] || style
}

const getBehaviorPatternText = (pattern) => {
  const texts = {
    active: '主动',
    passive: '被动',
    balanced: '平衡'
  }
  return texts[pattern] || pattern
}

onMounted(() => {
  loadCharacter()
})
</script>
