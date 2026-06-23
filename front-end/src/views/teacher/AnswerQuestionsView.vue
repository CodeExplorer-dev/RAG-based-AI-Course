<template>
  <div class="answer-page">
    <div class="page-head">
      <div class="page-head-left"><h2 class="page-title">回答问题</h2><p class="page-subtitle">查看并回答学生提问</p></div>
      <el-tag v-if="pendingCount > 0" type="warning" size="large" effect="dark" round>待回答：{{ pendingCount }} 条</el-tag>
      <el-tag v-else type="success" size="large" effect="dark" round>全部已回答</el-tag>
    </div>
    <div class="main-content">
      <el-card v-if="knowledgePoints.length" shadow="never" class="kp-card">
        <template #header><div class="card-header"><span><el-icon><TrendCharts /></el-icon> 高频知识点</span><span class="kp-total">共 {{ totalQuestions }} 条提问</span></div></template>
        <div class="kp-list">
          <div v-for="(kp, index) in knowledgePoints" :key="kp.name" class="kp-item">
            <span class="kp-rank">{{ index + 1 }}</span><span class="kp-name">{{ kp.name }}</span>
            <el-progress :percentage="Math.round(kp.count / knowledgePoints[0].count * 100)" :show-text="false" :stroke-width="8" class="kp-bar" />
            <span class="kp-count">{{ kp.count }} 次</span>
          </div>
        </div>
      </el-card>
      <el-card shadow="never" class="answer-card">
        <template #header><div class="card-header"><span><el-icon><ChatSquare /></el-icon> 学生提问列表</span><el-button text :icon="Refresh" @click="loadQuestions" :loading="loading">刷新</el-button></div></template>
        <template v-if="questions.length > 0">
          <div v-for="q in questions" :key="q.id" class="question-item">
            <div class="q-header"><div class="q-title">{{ q.title }}</div><el-tag size="small" :type="q.status === 'answered' ? 'success' : 'warning'" round>{{ q.status === 'answered' ? '已回答' : '待回答' }}</el-tag></div>
            <div class="q-meta"><span><el-icon :size="14"><User /></el-icon> {{ q.student_name || '未知' }}</span><span><el-icon :size="14"><Notebook /></el-icon> {{ q.course_name || '无课程' }}</span><span><el-icon :size="14"><Clock /></el-icon> {{ formatTime(q.created_at) }}</span></div>
            <div class="q-content">{{ q.content }}</div>
            <div v-if="q.answer" class="q-answer"><div class="answer-label">教师回答：</div><div>{{ q.answer }}</div></div>
            <div v-if="q.status === 'pending'" class="q-actions"><el-button type="primary" size="small" round @click="showAnswerDialog(q)"><el-icon><Edit /></el-icon> 写回答</el-button></div>
          </div>
        </template>
        <el-empty v-else :image-size="80" description="暂无学生提问" />
      </el-card>
    </div>
    <el-dialog v-model="dialogVisible" title="回答问题" width="600px" :close-on-click-modal="false" top="20vh">
      <div v-if="currentQuestion" class="dialog-question">
        <div class="dq-header"><strong>{{ currentQuestion.title }}</strong><el-tag size="small" type="info" round>{{ currentQuestion.course_name }}</el-tag></div>
        <div class="dq-student"><el-icon><User /></el-icon> {{ currentQuestion.student_name }} 提问于 {{ formatTime(currentQuestion.created_at) }}</div>
        <div class="dq-content">{{ currentQuestion.content }}</div>
      </div>
      <el-input v-model="answerText" type="textarea" :rows="5" placeholder="请输入你的回答..." class="answer-input" />
      <template #footer><el-button @click="dialogVisible = false">取消</el-button><el-button type="primary" :loading="answering" @click="submitAnswer" :disabled="!answerText.trim()">提交回答</el-button></template>
    </el-dialog>
  </div>
</template>
<script> let _kpCache = []; let _kpTotal = 0; export function clearKnowledgePointsCache() { _kpCache = []; _kpTotal = 0 } </script>
<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, User, Notebook, Clock, Edit, ChatSquare, TrendCharts } from '@element-plus/icons-vue'
import request from '../../api/request'
import { formatTime } from '../../utils/formatTime'
const loading = ref(false); const answering = ref(false); const questions = ref([]); const pendingCount = ref(0); const dialogVisible = ref(false); const currentQuestion = ref(null); const answerText = ref(''); const knowledgePoints = ref(_kpCache); const totalQuestions = ref(_kpTotal)
onMounted(() => { loadQuestions(); if (_kpCache.length > 0) { knowledgePoints.value = _kpCache; totalQuestions.value = _kpTotal } else loadKnowledgePoints() })
async function loadQuestions() { loading.value = true; try { const res = await request.get('/api/ask-teacher/pending'); const data = res.data || {}; questions.value = data.questions || []; pendingCount.value = data.pending_count || 0 } catch { questions.value = []; pendingCount.value = 0 }; loading.value = false }
async function loadKnowledgePoints() { try { const res = await request.get('/api/ask-teacher/knowledge-points'); const data = res.data || {}; _kpCache = data.knowledge_points || []; _kpTotal = data.total_questions || 0; knowledgePoints.value = _kpCache; totalQuestions.value = _kpTotal } catch { knowledgePoints.value = []; totalQuestions.value = 0 } }
function showAnswerDialog(q) { currentQuestion.value = q; answerText.value = ''; dialogVisible.value = true }
async function submitAnswer() { if (!answerText.value.trim()) return; answering.value = true; try { await request.put('/api/ask-teacher/' + currentQuestion.value.id + '/answer', { answer: answerText.value }); ElMessage.success('回答成功'); dialogVisible.value = false; questions.value = questions.value.filter(q => q.id !== currentQuestion.value.id); pendingCount.value = questions.value.filter(q => q.status === 'pending').length; loadKnowledgePoints(); if (pendingCount.value === 0) ElMessage.success('所有问题已回答完毕！') } finally { answering.value = false } }
</script>
<style scoped>
.answer-page { padding: 0; }
.page-head { display: flex; align-items: flex-end; justify-content: space-between; margin-bottom: 24px; }
.page-head-left {}
.page-title { font-size: 26px; font-weight: 700; color: var(--text-primary); margin: 0; letter-spacing: -0.5px; }
.page-title::after { content: ""; display: block; width: 36px; height: 3px; background: linear-gradient(90deg, #4a7cff, #7c5ce7); border-radius: 2px; margin-top: 8px; opacity: 0.4; }
.page-subtitle { font-size: 14px; color: var(--text-tertiary); margin-top: 4px; }
.main-content { display: flex; gap: 20px; align-items: flex-start; }
.answer-card { border-radius: 14px !important; flex: 1; min-width: 0; }
.card-header { display: flex; align-items: center; justify-content: space-between; font-size: 16px; font-weight: 600; }
.question-item { padding: 20px; border-bottom: 1px solid var(--border-light); transition: all var(--transition-fast); }
.question-item:last-child { border-bottom: none; }
.question-item:hover { background: #fafcff; }
.q-header { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }
.q-title { font-size: 17px; font-weight: 600; color: var(--text-primary); }
.q-meta { display: flex; align-items: center; gap: 16px; font-size: 13px; color: var(--text-tertiary); margin-bottom: 10px; }
.q-content { font-size: 14px; color: var(--text-secondary); background: #f7f8fa; padding: 12px 16px; border-radius: 8px; margin-bottom: 8px; line-height: 1.6; white-space: pre-wrap; }
.q-answer { font-size: 14px; color: var(--text-primary); background: #f0f9eb; padding: 12px 16px; border-radius: 8px; margin-bottom: 8px; line-height: 1.6; white-space: pre-wrap; border-left: 3px solid var(--success); }
.answer-label { color: var(--success); font-weight: 600; margin-bottom: 4px; }
.q-actions { margin-top: 8px; }
.dialog-question { background: #f7f8fa; padding: 16px; border-radius: 8px; margin-bottom: 16px; }
.dq-header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.dq-header strong { font-size: 16px; color: var(--text-primary); }
.dq-student { font-size: 13px; color: var(--text-tertiary); margin-bottom: 8px; display: flex; align-items: center; gap: 4px; }
.dq-content { font-size: 14px; color: var(--text-secondary); line-height: 1.6; white-space: pre-wrap; }
.kp-card { border-radius: 14px !important; width: 320px; flex-shrink: 0; }
.kp-total { font-size: 13px; color: var(--text-tertiary); font-weight: 400; }
.kp-list { padding: 0; }
.kp-item { display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px solid #f5f5f5; }
.kp-item:last-child { border-bottom: none; }
.kp-rank { width: 22px; height: 22px; border-radius: 50%; background: var(--primary); color: #fff; font-size: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.kp-item:nth-child(1) .kp-rank { background: var(--danger); }
.kp-item:nth-child(2) .kp-rank { background: var(--warning); }
.kp-item:nth-child(3) .kp-rank { background: var(--success); }
.kp-name { font-size: 14px; color: var(--text-primary); font-weight: 500; flex: 0 0 auto; }
.kp-bar { flex: 1; min-width: 80px; }
.kp-count { font-size: 13px; color: var(--text-tertiary); white-space: nowrap; }
</style>


