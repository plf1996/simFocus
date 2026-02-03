<template>
  <div>
    <div v-if="loading" class="text-center py-8">
      <div class="spinner mx-auto"></div>
    </div>

    <div v-else-if="!report" class="text-center py-8 text-gray-600">
      报告不存在或正在生成中
    </div>

    <div v-else class="space-y-6">
      <!-- Back Button -->
      <button
        @click="goBack"
        class="text-primary-600 hover:text-primary-700"
      >
        ← 返回讨论
      </button>

      <!-- Overview -->
      <div class="bg-white p-6 rounded-lg shadow-sm">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">讨论概览</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <div class="text-sm text-gray-500">议题</div>
            <div class="font-medium">{{ report.overview?.topic_title || '-' }}</div>
          </div>
          <div>
            <div class="text-sm text-gray-500">总轮次</div>
            <div class="font-medium">{{ report.overview?.total_rounds || 0 }}</div>
          </div>
          <div>
            <div class="text-sm text-gray-500">消息数</div>
            <div class="font-medium">{{ report.overview?.total_messages || 0 }}</div>
          </div>
          <div>
            <div class="text-sm text-gray-500">Token 使用</div>
            <div class="font-medium">{{ report.overview?.total_tokens_used || 0 }}</div>
          </div>
        </div>
      </div>

      <!-- LLM Summary (Markdown) -->
      <div v-if="report.summary" class="bg-white p-6 rounded-lg shadow-sm">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">AI 总结报告</h2>
        <div
          class="markdown-content prose prose-sm max-w-none"
          v-html="renderMarkdown(report.summary)"
        ></div>
      </div>

      <!-- Quality Scores -->
      <div class="bg-white p-6 rounded-lg shadow-sm">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">质量评分</h2>
        <div v-if="report.quality_scores" class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <div class="text-sm text-gray-500">深度</div>
            <div class="text-2xl font-bold text-primary-600">
              {{ report.quality_scores.depth || 0 }}
            </div>
          </div>
          <div>
            <div class="text-sm text-gray-500">多样性</div>
            <div class="text-2xl font-bold text-primary-600">
              {{ report.quality_scores.diversity || 0 }}
            </div>
          </div>
          <div>
            <div class="text-sm text-gray-500">建设性</div>
            <div class="text-2xl font-bold text-primary-600">
              {{ report.quality_scores.constructive || 0 }}
            </div>
          </div>
          <div>
            <div class="text-sm text-gray-500">连贯性</div>
            <div class="text-2xl font-bold text-primary-600">
              {{ report.quality_scores.coherence || 0 }}
            </div>
          </div>
        </div>
        <div v-else class="text-gray-500">
          质量评分数据不可用
        </div>
      </div>

      <!-- Viewpoints Summary -->
      <div class="bg-white p-6 rounded-lg shadow-sm">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">观点总结</h2>
        <div v-if="report.viewpoints_summary && report.viewpoints_summary.length > 0" class="space-y-4">
          <div
            v-for="viewpoint in report.viewpoints_summary"
            :key="viewpoint.character_id"
            class="border-l-4 border-primary-500 pl-4"
          >
            <h3 class="text-lg font-semibold text-gray-900">
              {{ viewpoint.character_name }}
            </h3>
            <p class="text-sm text-gray-500 mb-2">
              立场：{{ viewpoint.stance || '未知' }} | 发言：{{ viewpoint.message_count || 0 }} 次
            </p>
            <ul v-if="viewpoint.key_points && viewpoint.key_points.length > 0" class="list-disc list-inside text-gray-700">
              <li v-for="(point, idx) in viewpoint.key_points" :key="idx">
                {{ point }}
              </li>
            </ul>
          </div>
        </div>
        <div v-else class="text-gray-500">
          观点总结数据不可用
        </div>
      </div>

      <!-- Consensus -->
      <div v-if="report.consensus" class="bg-white p-6 rounded-lg shadow-sm">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">共识结论</h2>
        <div v-if="report.consensus.agreements && report.consensus.agreements.length > 0" class="space-y-4">
          <div>
            <h3 class="font-medium text-gray-900 mb-2">共同认同的观点</h3>
            <ul class="list-disc list-inside text-gray-700">
              <li v-for="(agreement, idx) in report.consensus.agreements" :key="idx">
                {{ agreement }}
              </li>
            </ul>
          </div>
          <div v-if="report.consensus.joint_recommendations && report.consensus.joint_recommendations.length > 0">
            <h3 class="font-medium text-gray-900 mb-2">共同建议</h3>
            <ul class="list-disc list-inside text-gray-700">
              <li v-for="(rec, idx) in report.consensus.joint_recommendations" :key="idx">
                {{ rec }}
              </li>
            </ul>
          </div>
        </div>
        <div v-else class="text-gray-500">
          未达成共识
        </div>
      </div>

      <!-- Controversies -->
      <div v-if="report.controversies && report.controversies.length > 0" class="bg-white p-6 rounded-lg shadow-sm">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">争议点</h2>
        <div class="space-y-4">
          <div
            v-for="(controversy, idx) in report.controversies"
            :key="idx"
            class="border-l-4 border-red-500 pl-4"
          >
            <h3 class="font-medium text-gray-900">
              {{ controversy.topic || `争议点 ${idx + 1}` }}
            </h3>
            <div v-if="controversy.viewpoints" class="mt-2">
              <div
                v-for="(points, charName) in controversy.viewpoints"
                :key="charName"
                class="text-sm text-gray-700"
              >
                <span class="font-medium">{{ charName }}：</span>
                <span>{{ Array.isArray(points) ? points.join('、') : points }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Insights & Recommendations -->
      <div v-if="report.insights || report.recommendations" class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div v-if="report.insights && report.insights.length > 0" class="bg-white p-6 rounded-lg shadow-sm">
          <h2 class="text-xl font-semibold text-gray-900 mb-4">关键洞察</h2>
          <ul class="space-y-2">
            <li v-for="(insight, idx) in report.insights" :key="idx" class="text-gray-700">
              • {{ insight.description || insight }}
            </li>
          </ul>
        </div>

        <div v-if="report.recommendations && report.recommendations.length > 0" class="bg-white p-6 rounded-lg shadow-sm">
          <h2 class="text-xl font-semibold text-gray-900 mb-4">行动建议</h2>
          <ul class="space-y-2">
            <li v-for="(rec, idx) in report.recommendations" :key="idx" class="text-gray-700">
              • {{ rec.action || rec }}
            </li>
          </ul>
        </div>
      </div>

      <!-- Full Transcript (Markdown) -->
      <div v-if="report.transcript" class="bg-white p-6 rounded-lg shadow-sm">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">完整讨论记录</h2>
        <div
          class="markdown-content prose prose-sm max-w-none"
          v-html="renderMarkdown(report.transcript)"
        ></div>
      </div>

      <!-- Actions -->
      <div class="flex justify-center gap-4">
        <button
          @click="regenerateReport"
          :disabled="regenerating"
          class="px-6 py-2 bg-white text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"
        >
          <span v-if="regenerating">重新生成中...</span>
          <span v-else>重新生成报告</span>
        </button>
        <button
          @click="exportReport"
          class="px-6 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
        >
          导出报告
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import endpoints from '@/services/endpoints'
import { marked } from 'marked'
import { useModal } from '@/composables/useModal'

const route = useRoute()
const router = useRouter()
const discussionId = route.params.id
const { showAlert, showConfirm, showToast } = useModal()

const report = ref(null)
const loading = ref(true)
const regenerating = ref(false)

// Configure marked for better output
marked.setOptions({
  breaks: true,  // Convert \n to <br>
  gfm: true,     // GitHub Flavored Markdown
})

const renderMarkdown = (content) => {
  if (!content) return ''
  try {
    return marked.parse(content)
  } catch (error) {
    console.error('Markdown parsing error:', error)
    return content
  }
}

const loadReport = async () => {
  try {
    const response = await endpoints.reports.getByDiscussionId(discussionId)
    report.value = response.data
  } catch (error) {
    console.error('Failed to load report:', error)
  } finally {
    loading.value = false
  }
}

const regenerateReport = async () => {
  const confirmed = await showConfirm(
    '确定要重新生成报告吗？',
    { title: '确认重新生成', confirmType: 'danger', confirmText: '重新生成' }
  )

  if (!confirmed) return

  regenerating.value = true
  try {
    await endpoints.reports.regenerate(discussionId)
    await loadReport()
    showToast('报告已重新生成', 'success')
  } catch (error) {
    console.error('Failed to regenerate report:', error)
    await showAlert('重新生成失败，请稍后重试', { title: '错误', confirmType: 'danger' })
  } finally {
    regenerating.value = false
  }
}

const exportReport = () => {
  if (!report.value) return

  // Simple text export (MVP)
  const content = JSON.stringify(report.value, null, 2)
  const blob = new Blob([content], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `report-${discussionId}.json`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

const goBack = () => {
  router.back()
}

onMounted(() => {
  loadReport()
})
</script>

<style scoped>
.markdown-content {
  color: #374151;
  line-height: 1.7;
}

.markdown-content :deep(h1) {
  font-size: 1.5rem;
  font-weight: 700;
  margin-top: 1.5rem;
  margin-bottom: 1rem;
  color: #111827;
}

.markdown-content :deep(h2) {
  font-size: 1.25rem;
  font-weight: 600;
  margin-top: 1.25rem;
  margin-bottom: 0.75rem;
  color: #111827;
}

.markdown-content :deep(h3) {
  font-size: 1.125rem;
  font-weight: 600;
  margin-top: 1rem;
  margin-bottom: 0.5rem;
  color: #111827;
}

.markdown-content :deep(h4) {
  font-size: 1rem;
  font-weight: 600;
  margin-top: 0.75rem;
  margin-bottom: 0.5rem;
  color: #111827;
}

.markdown-content :deep(p) {
  margin-bottom: 0.75rem;
}

.markdown-content :deep(ul), .markdown-content :deep(ol) {
  margin-left: 1.5rem;
  margin-bottom: 0.75rem;
}

.markdown-content :deep(li) {
  margin-bottom: 0.25rem;
}

.markdown-content :deep(code) {
  background-color: #f3f4f6;
  padding: 0.125rem 0.25rem;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}

.markdown-content :deep(pre) {
  background-color: #f3f4f6;
  padding: 1rem;
  border-radius: 0.5rem;
  overflow-x: auto;
  margin-bottom: 1rem;
}

.markdown-content :deep(pre code) {
  background-color: transparent;
  padding: 0;
}

.markdown-content :deep(blockquote) {
  border-left: 4px solid #d1d5db;
  padding-left: 1rem;
  margin-left: 0;
  margin-bottom: 0.75rem;
  color: #6b7280;
}

.markdown-content :deep(strong) {
  font-weight: 600;
}

.markdown-content :deep(a) {
  color: #2563eb;
  text-decoration: underline;
}

.markdown-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 1rem;
}

.markdown-content :deep(th), .markdown-content :deep(td) {
  border: 1px solid #e5e7eb;
  padding: 0.5rem;
  text-align: left;
}

.markdown-content :deep(th) {
  background-color: #f9fafb;
  font-weight: 600;
}
</style>
