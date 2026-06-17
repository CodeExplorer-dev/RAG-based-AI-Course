<template>
  <div class="stats-page">
    <div class="page-head">
      <h2 class="page-title">提问统计</h2>
    </div>
    <el-row :gutter="20" style="margin-bottom: 24px">
      <el-col :span="8" v-for="s in summaryStats" :key="s.label">
        <div class="stat-card">
          <div class="stat-icon" :style="{ background: s.bg }">
            <el-icon :size="24" :color="s.color"><component :is="s.icon" /></el-icon>
          </div>
          <div class="stat-body">
            <div class="stat-value">{{ s.value }}</div>
            <div class="stat-label">{{ s.label }}</div>
          </div>
        </div>
      </el-col>
    </el-row>
    <el-card shadow="never" class="stats-card">
      <template #header><span>高频提问</span></template>
      <el-table :data="topQuestions" v-loading="loading" stripe v-if="topQuestions.length">
        <el-table-column prop="title" label="问题" min-width="250" />
        <el-table-column prop="course_name" label="相关课程" width="160" />
        <el-table-column prop="created_at" label="提问时间" width="170" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'answered' ? 'success' : 'warning'" size="small" round>
              {{ row.status === 'answered' ? '已回答' : '待回答' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-else :image-size="80" description="暂无提问数据" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ChatDotRound, Message, Warning } from '@element-plus/icons-vue'
import request from '../api/request'

const loading = ref(false)
const topQuestions = ref([])
const summaryStats = ref([
  { label: '总提问数', value: 0, icon: 'ChatDotRound', bg: '#e6f7ff', color: '#1890ff' },
  { label: '已回答', value: 0, icon: 'Message', bg: '#f0f9eb', color: '#67c23a' },
  { label: '待回答', value: 0, icon: 'Warning', bg: '#fef0f0', color: '#f56c6c' },
])

onMounted(async () => {
  loading.value = true
  try {
    const [statsRes, questionsRes] = await Promise.all([
      request.get('/api/statistics'),
      request.get('/api/ask-teacher/mine')
    ])
    const stats = statsRes.data
    if (stats) {
      summaryStats.value[0].value = stats.total_questions || 0
    }
    const questions = questionsRes.data?.questions || []
    topQuestions.value = questions.sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).slice(0, 10)
    summaryStats.value[1].value = questions.filter(q => q.status === 'answered').length
    summaryStats.value[2].value = questions.filter(q => q.status === 'pending').length
  } catch { /* ignore */ }
  loading.value = false
})
</script>

<style scoped>
.stats-page { padding: 0; }
.page-head { margin-bottom: 24px; }
.page-title { font-size: 26px; font-weight: 600; color: #1d2129; margin: 0; }
.stat-card { background: #fff; border-radius: 8px; padding: 24px; display: flex; align-items: center; gap: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.stat-icon { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.stat-value { font-size: 28px; font-weight: 700; color: #1d2129; line-height: 1.2; }
.stat-label { font-size: 17px; color: #86909c; margin-top: 4px; }
.stats-card { border-radius: 8px; }
</style>
