<template>
  <div class="course-page">
    <div class="page-head">
      <h2 class="page-title">课程列表</h2>
      <el-button type="primary" :icon="Plus" plain @click="showJoinDialog = true">加入课程</el-button>
    </div>
    <div v-if="courses.length" class="course-grid">
      <div
        v-for="course in courses"
        :key="course.id"
        class="course-card"
        @click="enterCourse(course)"
      >
        <div class="card-accent"></div>
        <div class="card-body">
          <div class="card-icon">
            <el-icon :size="32" color="#409eff"><Reading /></el-icon>
          </div>
          <h3 class="card-title">{{ course.course_name }}</h3>
          <p class="card-desc">{{ course.description || '暂无描述' }}</p>
          <div class="card-footer">
            <el-tag size="small" type="info" round>
              加入码: {{ course.join_code }}
            </el-tag>
            <span class="student-count">{{ course.student_count || 0 }} 名学生</span>
          </div>
          <div class="card-actions">
            <el-button size="small" type="primary" plain @click.stop="goChat(course)">
              <el-icon><ChatDotRound /></el-icon>AI 问答
            </el-button>
            <el-button size="small" type="success" plain @click.stop="goCourseware(course)">
              <el-icon><FolderOpened /></el-icon>课件
            </el-button>
          </div>
        </div>
      </div>
    </div>
    <el-empty v-else :image-size="120" description="暂无课程，联系教师获取加入码">
      <el-button type="primary" :icon="Plus" @click="showJoinDialog = true">加入课程</el-button>
    </el-empty>

    <el-dialog v-model="showJoinDialog" title="加入课程" width="400px" :close-on-click-modal="false">
      <el-form :model="joinForm" label-width="0">
        <el-form-item>
          <el-input v-model="joinForm.code" placeholder="请输入课程加入码" size="large" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showJoinDialog = false">取消</el-button>
        <el-button type="primary" :loading="joining" @click="handleJoin">加入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Reading, Plus, ChatDotRound, FolderOpened } from '@element-plus/icons-vue'
import { listCourses, joinCourse } from '../api/course'

const router = useRouter()
const courses = ref([])
const showJoinDialog = ref(false)
const joinForm = ref({ code: '' })
const joining = ref(false)

onMounted(async () => {
  try {
    const res = await listCourses()
    // 后端返回 { code, message, data: { courses: [...] } }
    courses.value = res.data?.courses || []
  } catch {
    courses.value = []
  }
})

function enterCourse(course) {
  // 点击卡片默认进入课件管理
  goCourseware(course)
}

function goChat(course) {
  router.push(`/chat/${course.id}`)
}

function goCourseware(course) {
  router.push(`/courseware?course_id=${course.id}`)
}

async function handleJoin() {
  if (!joinForm.value.code) return
  joining.value = true
  try {
    await joinCourse(joinForm.value.code)
    ElMessage.success('加入成功')
    showJoinDialog.value = false
    joinForm.value.code = ''
    // 重新加载课程列表
    const res = await listCourses()
    courses.value = res.data?.courses || []
  } catch {
    // 错误已在拦截器中处理
  } finally {
    joining.value = false
  }
}
</script>

<style scoped>
.course-page { padding: 0; }
.page-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}
.page-title { font-size: 26px; font-weight: 600; color: #1d2129; margin: 0; }
.course-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 20px;
}
.course-card {
  background: #fff;
  border-radius: 8px;
  cursor: pointer;
  overflow: hidden;
  transition: box-shadow 0.25s, transform 0.25s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}
.course-card:nth-child(1) .card-accent { background: linear-gradient(90deg, #5b8def, #667eea); }
.course-card:nth-child(2) .card-accent { background: linear-gradient(90deg, #67c23a, #85ce61); }
.course-card:nth-child(3) .card-accent { background: linear-gradient(90deg, #f56c6c, #e6a23c); }
.course-card:nth-child(4) .card-accent { background: linear-gradient(90deg, #909399, #b0b3b8); }
.course-card:nth-child(5) .card-accent { background: linear-gradient(90deg, #e6a23c, #f56c6c); }
.course-card:nth-child(6) .card-accent { background: linear-gradient(90deg, #5b8def, #67c23a); }
.course-card:hover {
  box-shadow: 0 8px 24px rgba(91, 141, 239, 0.12);
  transform: translateY(-3px);
}
.card-accent { height: 4px; }
.card-body { padding: 20px; }
.card-icon { text-align: center; margin-bottom: 12px; }
.card-title { font-size: 20px; font-weight: 600; text-align: center; margin: 0 0 6px; color: #1d2129; }
.card-desc { font-size: 17px; color: #86909c; text-align: center; margin: 0 0 16px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.card-footer { display: flex; align-items: center; justify-content: center; gap: 12px; margin-bottom: 12px; }
.card-actions { display: flex; gap: 8px; justify-content: center; }
.student-count { font-size: 16px; color: #86909c; }
</style>
