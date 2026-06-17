<template>
  <div class="tstats-page">
    <div class="page-head">
      <h2 class="page-title">教学统计</h2>
    </div>
    <el-row :gutter="20" style="margin-bottom: 24px">
      <el-col :span="6" v-for="s in stats" :key="s.label">
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
    <el-card shadow="never" class="stats-card" style="margin-bottom: 20px">
      <template #header><span>待回答问题</span></template>
      <el-table :data="pendingQuestions" v-loading="loading" stripe>
        <el-table-column prop="title" label="问题" min-width="200" />
        <el-table-column prop="student_name" label="提问学生" width="120" />
        <el-table-column prop="course_name" label="课程" width="140" />
        <el-table-column label="提问时间" width="170">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="160" align="center">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="showAnswerDialog(row)">回答</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && !pendingQuestions.length" :image-size="60" description="暂无疑问" />
    </el-card>

    <el-dialog v-model="dialogVisible" title="回答问题" width="560px">
      <div style="margin-bottom: 12px; font-weight: 500">{{ currentQuestion?.title }}</div>
      <div style="margin-bottom: 16px; color: #606266; font-size: 14px; background: #f7f8fa; padding: 12px; border-radius: 6px;">
        {{ currentQuestion?.content }}
      </div>
      <el-input v-model="answerText" type="textarea" :rows="4" placeholder="输入回答内容..." />
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="answering" @click="submitAnswer">提交回答</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Notebook, FolderOpened, Message, Warning } from '@element-plus/icons-vue'
import request from '../../api/request'
import { formatTime } from '../../utils/formatTime'
import { listCourses } from '../../api/course'

const loading = ref(false)
const answering = ref(false)
const dialogVisible = ref(false)
const currentQuestion = ref(null)
const answerText = ref('')
const pendingQuestions = ref([])
const stats = ref([
  { label: '我的课程', value: 0, icon: 'Notebook', bg: '#e6f7ff', color: '#1890ff' },
  { label: '课件总数', value: 0, icon: 'FolderOpened', bg: '#f0f9eb', color: '#67c23a' },
  { label: '总提问', value: 0, icon: 'Message', bg: '#fef0f0', color: '#f56c6c' },
  { label: '待回答', value: 0, icon: 'Warning', bg: '#fff7e6', color: '#e6a23c' },
])

onMounted(async () => {
  loading.value = true
  try {
    const res = await listCourses()
    const courses = res.data?.courses || []
    const myCourses = courses.filter(c => c.role === 'teacher')
    stats.value[0].value = myCourses.length
    let totalCw = 0
    for (const c of myCourses) { totalCw += c.courseware_count || 0 }
    stats.value[1].value = totalCw

    for (const c of myCourses) {
      try {
        const qRes = await request.get('/api/ask-teacher/course/' + c.id)
        const qs = qRes.data?.questions || []
        qs.forEach(q => { stats.value[2].value++; if (q.status === 'pending') pendingQuestions.value.push(q) })
      } catch { /* ignore */ }
    }
    stats.value[3].value = pendingQuestions.value.length
  } catch { /* ignore */ }
  loading.value = false
})

function showAnswerDialog(q) {
  currentQuestion.value = q
  answerText.value = ''
  dialogVisible.value = true
}

async function submitAnswer() {
  if (!answerText.value.trim()) { ElMessage.warning('请输入回答内容'); return }
  answering.value = true
  try {
    await request.put('/api/ask-teacher/' + currentQuestion.value.id + '/answer', { answer: answerText.value })
    ElMessage.success('回答成功')
    dialogVisible.value = false
    pendingQuestions.value = pendingQuestions.value.filter(q => q.id !== currentQuestion.value.id)
    stats.value[3].value = pendingQuestions.value.length
  } finally { answering.value = false }
}
</script>

<style scoped>
.tstats-page { padding: 0; }
.page-head { margin-bottom: 24px; }
.page-title { font-size: 26px; font-weight: 600; color: #1d2129; margin: 0; }
.stat-card { background: #fff; border-radius: 8px; padding: 24px; display: flex; align-items: center; gap: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.stat-icon { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.stat-value { font-size: 28px; font-weight: 700; color: #1d2129; line-height: 1.2; }
.stat-label { font-size: 17px; color: #86909c; margin-top: 4px; }
.stats-card { border-radius: 8px; }
</style>
