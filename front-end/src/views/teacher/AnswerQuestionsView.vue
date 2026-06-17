<template>
  <div class="answer-page">
    <div class="page-head">
      <h2 class="page-title">回答问题</h2>
      <el-tag v-if="pendingCount > 0" type="warning" size="large" effect="dark" round>
        待回答：{{ pendingCount }} 条
      </el-tag>
      <el-tag v-else type="success" size="large" effect="dark" round>
        全部已回答
      </el-tag>
    </div>

    <el-card shadow="never" class="answer-card">
      <template #header>
        <div class="card-header">
          <span>学生提问列表</span>
          <el-button text :icon="Refresh" @click="loadQuestions" :loading="loading">刷新</el-button>
        </div>
      </template>

      <template v-if="questions.length > 0">
        <div v-for="q in questions" :key="q.id" class="question-item">
          <div class="q-header">
            <div class="q-title">{{ q.title }}</div>
            <el-tag size="small" :type="q.status === 'answered' ? 'success' : 'warning'" round>
              {{ q.status === 'answered' ? '已回答' : '待回答' }}
            </el-tag>
          </div>
          <div class="q-meta">
            <span><el-icon :size="14"><User /></el-icon> {{ q.student_name || '未知' }}</span>
            <span><el-icon :size="14"><Notebook /></el-icon> {{ q.course_name || '无课程' }}</span>
            <span><el-icon :size="14"><Clock /></el-icon> {{ q.created_at }}</span>
          </div>
          <div class="q-content">{{ q.content }}</div>
          <div v-if="q.answer" class="q-answer">
            <div class="answer-label">教师回答：</div>
            <div>{{ q.answer }}</div>
          </div>
          <div v-if="q.status === 'pending'" class="q-actions">
            <el-button type="primary" size="small" @click="showAnswerDialog(q)">
              <el-icon><Edit /></el-icon> 写回答
            </el-button>
          </div>
        </div>
      </template>

      <el-empty v-else :image-size="80" description="暂无学生提问">
        <template #description>
          <p>还没有学生向你提问</p>
        </template>
      </el-empty>
    </el-card>

    <el-dialog v-model="dialogVisible" title="回答问题" width="600px" :close-on-click-modal="false">
      <div v-if="currentQuestion" class="dialog-question">
        <div class="dq-header">
          <strong>{{ currentQuestion.title }}</strong>
          <el-tag size="small" type="info" round>{{ currentQuestion.course_name }}</el-tag>
        </div>
        <div class="dq-student">
          <el-icon><User /></el-icon> {{ currentQuestion.student_name }} 提问于 {{ currentQuestion.created_at }}
        </div>
        <div class="dq-content">{{ currentQuestion.content }}</div>
      </div>
      <el-input
        v-model="answerText"
        type="textarea"
        :rows="5"
        placeholder="请输入你的回答..."
        class="answer-input"
      />
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="answering" @click="submitAnswer" :disabled="!answerText.trim()">
          提交回答
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, User, Notebook, Clock, Edit } from '@element-plus/icons-vue'
import request from '../../api/request'

const loading = ref(false)
const answering = ref(false)
const questions = ref([])
const pendingCount = ref(0)
const dialogVisible = ref(false)
const currentQuestion = ref(null)
const answerText = ref('')

onMounted(() => {
  loadQuestions()
})

async function loadQuestions() {
  loading.value = true
  try {
    const res = await request.get('/api/ask-teacher/pending')
    const data = res.data || {}
    questions.value = data.questions || []
    pendingCount.value = data.pending_count || 0
  } catch {
    questions.value = []
    pendingCount.value = 0
  }
  loading.value = false
}

function showAnswerDialog(q) {
  currentQuestion.value = q
  answerText.value = ''
  dialogVisible.value = true
}

async function submitAnswer() {
  if (!answerText.value.trim()) return
  answering.value = true
  try {
    await request.put('/api/ask-teacher/' + currentQuestion.value.id + '/answer', { answer: answerText.value })
    ElMessage.success('回答成功')
    dialogVisible.value = false
    questions.value = questions.value.filter(q => q.id !== currentQuestion.value.id)
    pendingCount.value = questions.value.filter(q => q.status === 'pending').length
    if (pendingCount.value === 0) {
      ElMessage.success('所有问题已回答完毕！')
    }
  } finally {
    answering.value = false
  }
}
</script>

<style scoped>
.answer-page { padding: 0; }
.page-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}
.page-title { font-size: 26px; font-weight: 600; color: #1d2129; margin: 0; }
.answer-card { border-radius: 8px; }
.card-header { display: flex; align-items: center; justify-content: space-between; font-size: 16px; font-weight: 600; }
.question-item {
  padding: 20px;
  border-bottom: 1px solid #f0f0f5;
  transition: background 0.2s;
}
.question-item:last-child { border-bottom: none; }
.question-item:hover { background: #fafcff; }
.q-header { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }
.q-title { font-size: 18px; font-weight: 600; color: #1d2129; }
.q-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 14px;
  color: #909399;
  margin-bottom: 10px;
}
.q-meta span { display: flex; align-items: center; gap: 4px; }
.q-content {
  font-size: 15px;
  color: #606266;
  background: #f7f8fa;
  padding: 12px 16px;
  border-radius: 6px;
  margin-bottom: 8px;
  line-height: 1.6;
  white-space: pre-wrap;
}
.q-answer {
  font-size: 15px;
  color: #1d2129;
  background: #f0f9eb;
  padding: 12px 16px;
  border-radius: 6px;
  margin-bottom: 8px;
  line-height: 1.6;
  white-space: pre-wrap;
}
.answer-label { color: #67c23a; font-weight: 600; margin-bottom: 4px; }
.q-actions { margin-top: 8px; }
.dialog-question {
  background: #f7f8fa;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 16px;
}
.dq-header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.dq-header strong { font-size: 16px; color: #1d2129; }
.dq-student { font-size: 13px; color: #909399; margin-bottom: 8px; display: flex; align-items: center; gap: 4px; }
.dq-content { font-size: 15px; color: #606266; line-height: 1.6; white-space: pre-wrap; }
.answer-input { margin-top: 8px; }
</style>
