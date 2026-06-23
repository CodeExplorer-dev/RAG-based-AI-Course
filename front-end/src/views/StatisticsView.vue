<template>
  <div class="stats-page">
    <div class="page-head">
      <div class="page-head-left">
        <h2 class="page-title">提问统计</h2>
        <p class="page-subtitle">了解你的提问情况和回答进展</p>
      </div>
    </div>
    <el-row :gutter="20" style="margin-bottom: 28px">
      <el-col :span="8" v-for="s in summaryStats" :key="s.label">
        <div class="stat-card">
          <div class="stat-icon-wrap" :style="{ background: s.bg }"><el-icon :size="22" :color="s.color"><component :is="s.icon" /></el-icon></div>
          <div class="stat-body">
            <div class="stat-value">{{ s.value }}</div>
            <div class="stat-label">{{ s.label }}</div>
          </div>
          <div class="stat-glow" :style="{ background: s.color }"></div>
        </div>
      </el-col>
    </el-row>
    <el-card shadow="never" class="stats-card">
      <template #header><span class="card-title-hd"><el-icon><DataAnalysis /></el-icon> 高频提问</span></template>
      <el-table :data="topQuestions" v-loading="loading" stripe size="large" v-if="topQuestions.length">
        <el-table-column prop="title" label="问题" min-width="250" />
        <el-table-column prop="course_name" label="相关课程" width="160" />
        <el-table-column label="提问时间" width="170"><template #default="{ row }">{{ formatTime(row.created_at) }}</template></el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }"><el-tag :type="row.status === 'answered' ? 'success' : 'warning'" size="small" round>{{ row.status === 'answered' ? '已回答' : '待回答' }}</el-tag></template>
        </el-table-column>
      </el-table>
      <el-empty v-else :image-size="80" description="暂无提问数据" />
    </el-card>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { ChatDotRound, Message, Warning, DataAnalysis } from '@element-plus/icons-vue'
import request from '../api/request'
import { formatTime } from '../utils/formatTime'
const loading = ref(false); const topQuestions = ref([])
const summaryStats = ref([{ label: '总提问数', value: 0, icon: 'ChatDotRound', bg: '#e6f7ff', color: '#1890ff' }, { label: '已回答', value: 0, icon: 'Message', bg: '#f0f9eb', color: '#67c23a' }, { label: '待回答', value: 0, icon: 'Warning', bg: '#fef0f0', color: '#f56c6c' }])
onMounted(async () => { loading.value = true; try { const [statsRes, questionsRes] = await Promise.all([request.get('/api/statistics'), request.get('/api/ask-teacher/mine')]); const stats = statsRes.data; if (stats) { summaryStats.value[0].value = stats.total_questions || 0 }; const questions = questionsRes.data?.questions || []; topQuestions.value = questions.sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).slice(0, 10); summaryStats.value[1].value = questions.filter(q => q.status === 'answered').length; summaryStats.value[2].value = questions.filter(q => q.status === 'pending').length } catch {}; loading.value = false })
</script>
<style scoped>
.stats-page { padding: 0; }
.page-head { margin-bottom: 24px; }
.page-title { font-size: 26px; font-weight: 700; color: var(--text-primary); margin: 0; letter-spacing: -0.5px; }
.page-title::after { content: ""; display: block; width: 40px; height: 3px; background: linear-gradient(90deg, #4a7cff,#52b859); border-radius: 2px; margin-top: 8px; opacity: 0.5; } 
.page-subtitle { font-size: 14px; color: var(--text-tertiary); margin-top: 4px; }
.card-title-hd { display: flex; align-items: center; gap: 6px; font-size: 16px; font-weight: 600; }
.stat-card { background: var(--bg-card); border-radius: 14px; padding: 24px; display: flex; align-items: center; gap: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border: 1px solid var(--border-light); transition: all var(--transition-normal); position: relative; overflow: hidden; }
.stat-card:hover { box-shadow: 0 8px 24px rgba(0,0,0,0.08); transform: translateY(-2px); }
.stat-glow { position: absolute; top: 0; left: 0; width: 100%; height: 3px; opacity: 0.6; }
.stat-icon-wrap { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.stat-value { font-size: 28px; font-weight: 700; color: var(--text-primary); line-height: 1.2; }
.stat-label { font-size: 14px; color: var(--text-tertiary); margin-top: 4px; }
.stats-card { border-radius: 14px !important; }
</style>

