<template>
  <div class="ask-page">
    <div class="page-head">
      <div class="page-head-left">
        <h2 class="page-title">向老师提问</h2>
        <p class="page-subtitle">如果 AI 回答不够准确，可以直接向老师提问</p>
      </div>
    </div>
    <el-row :gutter="24">
      <el-col :span="14">
        <el-card shadow="never" class="ask-card">
          <template #header><span class="card-title-hd"><el-icon><Edit /></el-icon> 提交问题</span></template>
          <el-form :model="form" label-width="0">
            <el-form-item><el-input v-model="form.title" placeholder="问题标题" size="large" clearable class="ask-input" /></el-form-item>
            <el-form-item><el-select v-model="form.course_id" placeholder="选择相关课程" size="large" clearable style="width:100%"><el-option v-for="c in courses" :key="c.id" :label="c.course_name" :value="c.id" /></el-select></el-form-item>
            <el-form-item><el-input v-model="form.content" type="textarea" :rows="6" placeholder="详细描述你的问题..." class="ask-textarea" /></el-form-item>
            <el-form-item><el-button type="primary" size="large" :loading="submitting" @click="submitQuestion" round>提交问题</el-button></el-form-item>
          </el-form>
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card shadow="never" class="history-card">
          <template #header>
            <div class="card-head-between">
              <span class="card-title-hd"><el-icon><Clock /></el-icon> 我的提问历史</span>
              <el-button v-if="myQuestions.length" text type="danger" size="small" :loading="clearing" @click="clearAll"><el-icon><Delete /></el-icon> 一键清除</el-button>
            </div>
          </template>
          <div v-if="myQuestions.length" class="history-list">
            <div v-for="q in myQuestions" :key="q.id" class="history-item">
              <div class="history-item-head">
                <div class="history-title">{{ q.title }}</div>
                <el-tag size="small" :type="q.status === 'answered' ? 'success' : 'warning'" round>{{ q.status === 'answered' ? '已回复' : '待回复' }}</el-tag>
              </div>
              <div class="history-meta"><el-icon :size="13"><Clock /></el-icon> {{ formatTime(q.created_at) }}</div>
              <div v-if="q.answer" class="history-answer"><div class="answer-label">教师回复：</div><div class="answer-text">{{ q.answer }}</div></div>
            </div>
          </div>
          <el-empty v-else :image-size="60" description="还没有提过问" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Edit, Clock, Delete } from '@element-plus/icons-vue'
import request from '../api/request'
import { formatTime } from '../utils/formatTime'
const courses = ref([]); const myQuestions = ref([]); const submitting = ref(false); const clearing = ref(false); const form = ref({ title: '', course_id: '', content: '' })
onMounted(async () => { try { const [cRes, qRes] = await Promise.all([request.get('/api/courses'), request.get('/api/ask-teacher/mine')]); courses.value = cRes.data?.courses || []; myQuestions.value = qRes.data?.questions || [] } catch {} })
async function clearAll() { if (myQuestions.value.length === 0) return; clearing.value = true; try { await request.delete('/api/ask-teacher/mine'); ElMessage.success('已清空所有提问'); myQuestions.value = [] } finally { clearing.value = false } }
async function submitQuestion() { if (!form.value.title || !form.value.content) { ElMessage.warning('请填写问题标题和内容'); return }; submitting.value = true; try { await request.post('/api/ask-teacher', form.value); ElMessage.success('问题已提交，等待老师回复'); form.value = { title: '', course_id: '', content: '' }; const qRes = await request.get('/api/ask-teacher/mine'); myQuestions.value = qRes.data?.questions || [] } finally { submitting.value = false } }
</script>
<style scoped>
.ask-page { padding: 0; }
.page-head { margin-bottom: 24px; }
.page-title { font-size: 26px; font-weight: 700; color: var(--text-primary); margin: 0; letter-spacing: -0.5px; }
.page-title::after { content: ""; display: block; width: 40px; height: 3px; background: linear-gradient(90deg, #e8923a,#4a7cff); border-radius: 2px; margin-top: 8px; opacity: 0.5; } 
.page-subtitle { font-size: 14px; color: var(--text-tertiary); margin-top: 4px; }
.card-title-hd { display: flex; align-items: center; gap: 6px; font-size: 16px; font-weight: 600; }
.card-head-between { display: flex; align-items: center; justify-content: space-between; }
.ask-card, .history-card { border-radius: 14px !important; }
.ask-input :deep(.el-input__wrapper) { border-radius: 10px; }
.ask-textarea :deep(.el-textarea__inner) { border-radius: 10px; }
.history-list { max-height: 500px; overflow-y: auto; }
.history-item { padding: 16px 0; border-bottom: 1px solid var(--border-light); transition: all var(--transition-fast); }
.history-item:last-child { border-bottom: none; }
.history-item:hover { background: #fafcff; padding-left: 8px; border-radius: 6px; }
.history-item-head { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.history-title { font-size: 16px; font-weight: 500; color: var(--text-primary); }
.history-meta { font-size: 13px; color: var(--text-tertiary); margin-bottom: 8px; display: flex; align-items: center; gap: 4px; }
.history-answer { font-size: 14px; color: var(--text-secondary); background: #f7f8fa; padding: 10px 14px; border-radius: 8px; border-left: 3px solid var(--success); }
.answer-label { color: var(--success); font-weight: 500; margin-bottom: 4px; }
.answer-text { line-height: 1.6; }
</style>

