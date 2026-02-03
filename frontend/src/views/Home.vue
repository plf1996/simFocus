<template>
  <div class="text-center py-20">
    <h1 class="text-5xl font-bold text-gray-900 mb-6">
      AI 虚拟焦点小组平台
    </h1>
    <p class="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
      通过模拟多角色实时讨论，快速获得多元视角、深度洞察和创意灵感
    </p>

    <div class="flex justify-center gap-4">
      <router-link
        v-if="!isAuthenticated"
        to="/register"
        class="bg-primary-600 text-white px-8 py-3 rounded-lg font-medium hover:bg-primary-700 transition-colors"
      >
        立即开始
      </router-link>
      <router-link
        to="/topics"
        class="bg-white text-gray-700 border border-gray-300 px-8 py-3 rounded-lg font-medium hover:bg-gray-50 transition-colors"
      >
        浏览议题
      </router-link>
    </div>

    <div class="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
      <div class="bg-white p-6 rounded-lg shadow-sm">
        <div class="text-primary-600 mb-4">
          <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-gray-900 mb-2">多视角碰撞</h3>
        <p class="text-gray-600">
          单次讨论获得 3-7 个不同角色的观点，节省时间成本
        </p>
      </div>

      <div class="bg-white p-6 rounded-lg shadow-sm">
        <div class="text-primary-600 mb-4">
          <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-gray-900 mb-2">实时观察</h3>
        <p class="text-gray-600">
          观看观点的形成、碰撞与演变过程，而不仅仅是结论
        </p>
      </div>

      <div class="bg-white p-6 rounded-lg shadow-sm">
        <div class="text-primary-600 mb-4">
          <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-gray-900 mb-2">深度洞察</h3>
        <p class="text-gray-600">
          自动生成结构化报告，提取共识、争议和行动建议
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const isAuthenticated = computed(() => authStore.isAuthenticated)
</script>
