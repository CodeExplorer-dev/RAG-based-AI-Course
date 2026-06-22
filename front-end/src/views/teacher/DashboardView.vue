<template>
  <div class="dashboard-page">
    <div class="page-head">
      <div class="page-head-left"><h2 class="page-title">教师面板</h2><p class="page-subtitle">欢迎回来，{{ userStore.userInfo?.username }}</p></div>
    </div>
    <div class="stats-grid">
      <div class="stat-card" v-for="s in stats" :key="s.label">
        <div class="stat-glow" :style="{ background: s.color }"></div>
        <div class="stat-icon-wrap" :style="{ background: s.bg }"><el-icon :size="22" :color="s.color"><component :is="s.icon" /></el-icon></div>
        <div class="stat-body"><div class="stat-value">{{ s.value }}</div><div class="stat-label">{{ s.label }}</div></div>
      </div>
    </div>
    <div class="action-grid">
      <div class="action-card" @click="$router.push('/teacher/courses')">
        <div class="action-icon" style="background:linear-gradient(135deg,#e6f7ff,#cceeff);"><el-icon :size="28" color="#1890ff"><Notebook /></el-icon></div>
        <span>课程管理</span>
      </div>
      <div class="action-card" @click="$router.push('/teacher/courseware')">
        <div class="action-icon" style="background:linear-gradient(135deg,#f0f9eb,#ddf5d5);"><el-icon :size="28" color="#67c23a"><FolderOpened /></el-icon></div>
        <span>上传课件</span>
      </div>
      <div class="action-card" @click="$router.push('/courses')">
        <div class="action-icon" style="background:linear-gradient(135deg,#fef6e6,#fde8b3);"><el-icon :size="28" color="#e6a23c"><Reading /></el-icon></div>
        <span>查看课程</span>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '../../stores/user'
import { Notebook, FolderOpened, Reading } from '@element-plus/icons-vue'
import { listCourses } from '../../api/course'
const userStore = useUserStore()
const stats = ref([{ label: '我的课程', value: 0, icon: 'Notebook', bg: '#e6f7ff', color: '#1890ff' }, { label: '课件总数', value: 0, icon: 'FolderOpened', bg: '#f0f9eb', color: '#67c23a' }, { label: '学生总数', value: 0, icon: 'Reading', bg: '#fef0f0', color: '#f56c6c' }])
onMounted(async () => { try { const res = await listCourses(); const courses = res.data?.courses || []; const myCourses = courses.filter(c => c.role === 'teacher'); stats.value[0].value = myCourses.length; let totalCw = 0, totalStu = 0; myCourses.forEach(c => { totalCw += c.courseware_count || 0; totalStu += c.student_count || 0 }); stats.value[1].value = totalCw; stats.value[2].value = totalStu } catch {} })
</script>
<style scoped>
.dashboard-page { padding: 0; }
.page-head { margin-bottom: 28px; position: relative; }
.page-head::before { content: ""; position: absolute; top: -4px; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, #52b859,#4a7cff); border-radius: 2px; opacity: 0.4; }
.page-title { font-size: 26px; font-weight: 700; color: var(--text-primary); margin: 0; letter-spacing: -0.5px; }
.page-title::after { content: ""; display: block; width: 36px; height: 3px; background: linear-gradient(90deg, #4a7cff, #7c5ce7); border-radius: 2px; margin-top: 8px; opacity: 0.4; }
.page-subtitle { font-size: 14px; color: var(--text-tertiary); margin-top: 4px; }
.stats-deco { height: 3px; background: linear-gradient(90deg, #4a7cff, #7c5ce7, #52b859, #e8923a); border-radius: 2px; margin-bottom: 24px; opacity: 0.5; }
.stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 28px; }
.stat-card { background: var(--bg-card); border-radius: 14px; padding: 24px; display: flex; align-items: center; gap: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border: 1px solid var(--border-light); transition: all var(--transition-normal); position: relative; overflow: hidden; }
.stat-card:hover { box-shadow: 0 8px 24px rgba(0,0,0,0.08); transform: translateY(-2px); }
.stat-glow { position: absolute; top: 0; left: 0; width: 100%; height: 3px; opacity: 0.6; }
.stat-icon-wrap { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.stat-value { font-size: 28px; font-weight: 700; color: var(--text-primary); line-height: 1.2; }
.stat-label { font-size: 14px; color: var(--text-tertiary); margin-top: 4px; }
.action-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.action-card { background: var(--bg-card); border-radius: 14px; padding: 32px 20px; text-align: center; cursor: pointer; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border: 1px solid var(--border-light); transition: all var(--transition-normal); }
.action-card:hover { box-shadow: 0 8px 24px rgba(0,0,0,0.08); transform: translateY(-4px); }
.action-icon { width: 56px; height: 56px; border-radius: 14px; display: flex; align-items: center; justify-content: center; margin: 0 auto 14px; }
.action-card span { font-size: 16px; font-weight: 500; color: var(--text-primary); }
</style>



