 <template>
   <div class="dashboard-page">
     <div class="page-head">
       <h2 class="page-title">教师面板</h2>
       <span class="page-desc">欢迎回来，{{ userStore.userInfo?.username }}</span>
     </div>
     <div class="stats-grid">
       <div class="stat-card" v-for="s in stats" :key="s.label">
         <div class="stat-icon" :style="{ background: s.bg }">
           <el-icon :size="24" :color="s.color"><component :is="s.icon" /></el-icon>
         </div>
         <div class="stat-body">
           <div class="stat-value">{{ s.value }}</div>
           <div class="stat-label">{{ s.label }}</div>
         </div>
       </div>
     </div>
     <div class="action-grid">
       <div class="action-card" @click="$router.push('/teacher/courses')">
         <el-icon :size="28" color="#5b8def"><Notebook /></el-icon>
         <span>创建课程</span>
       </div>
       <div class="action-card" @click="$router.push('/teacher/courseware')">
         <el-icon :size="28" color="#67c23a"><FolderOpened /></el-icon>
         <span>上传课件</span>
       </div>
       <div class="action-card" @click="$router.push('/teacher/statistics')">
         <el-icon :size="28" color="#e6a23c"><DataAnalysis /></el-icon>
         <span>查看统计</span>
       </div>
       <div class="action-card" @click="$router.push('/teacher/chat')">
         <el-icon :size="28" color="#5b8def"><ChatDotRound /></el-icon>
         <span>测试问答</span>
       </div>
     </div>
   </div>
 </template>
 
 <script setup>
 import { ref, onMounted } from 'vue'
 import { useUserStore } from '../../stores/user'
 import { Notebook, FolderOpened, DataAnalysis, ChatDotRound, Reading, Share } from '@element-plus/icons-vue'
 import request from '../../api/request'
 
 const userStore = useUserStore()
 const stats = ref([
   { label: '我的课程', value: 0, icon: 'Notebook', bg: '#e6f7ff', color: '#1890ff' },
   { label: '课件数量', value: 0, icon: 'FolderOpened', bg: '#f0f9eb', color: '#67c23a' },
   { label: '学生提问', value: 0, icon: 'ChatDotRound', bg: '#fef0f0', color: '#f56c6c' },
   { label: '知识点数', value: 0, icon: 'Share', bg: '#fdf6ec', color: '#e6a23c' },
 ])
 
 onMounted(async () => {
   try {
     const res = await request.get('/api/teacher/stats')
     if (res) {
       stats.value[0].value = res.courses || 0
       stats.value[1].value = res.courseware || 0
       stats.value[2].value = res.questions || 0
       stats.value[3].value = res.knowledge_points || 0
     }
   } catch { /* ignore */ }
 })
 </script>
 
 <style scoped>
 .dashboard-page { padding: 0; }
 .page-head { margin-bottom: 24px; }
 .page-title { font-size: 20px; font-weight: 600; color: #1d2129; margin: 0 0 4px; }
 .page-desc { font-size: 14px; color: #86909c; }
 .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 24px; }
 .stat-card { background: #fff; border-radius: 8px; padding: 24px; display: flex; align-items: center; gap: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); transition: box-shadow 0.2s; }
 .stat-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.08); }
 .stat-icon { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
 .stat-value { font-size: 24px; font-weight: 700; color: #1d2129; line-height: 1.2; }
 .stat-label { font-size: 13px; color: #86909c; margin-top: 4px; }
 .action-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
 .action-card { background: #fff; border-radius: 8px; padding: 28px 20px; text-align: center; cursor: pointer; box-shadow: 0 1px 3px rgba(0,0,0,0.06); transition: box-shadow 0.2s, transform 0.2s; }
 .action-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.1); transform: translateY(-2px); }
 .action-card span { display: block; margin-top: 12px; font-size: 14px; font-weight: 500; color: #1d2129; }
 </style>
