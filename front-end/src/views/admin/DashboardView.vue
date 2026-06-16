 <template>
   <div class="ad-page">
     <div class="page-head">
       <h2 class="page-title">管理面板</h2>
       <span class="page-desc">系统运行概况</span>
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
     <el-row :gutter="20">
       <el-col :span="12">
         <el-card shadow="never" class="manage-card">
           <template #header><span><el-icon><User /></el-icon> 用户管理</span></template>
           <el-button type="primary" plain @click="$router.push('/admin/users')">管理用户</el-button>
         </el-card>
       </el-col>
       <el-col :span="12">
         <el-card shadow="never" class="manage-card">
           <template #header><span><el-icon><Notebook /></el-icon> 课程管理</span></template>
           <el-button type="primary" plain @click="$router.push('/admin/courses')">管理课程</el-button>
         </el-card>
       </el-col>
     </el-row>
   </div>
 </template>
 
 <script setup>
 import { ref, onMounted } from 'vue'
 import { UserFilled, Notebook, ChatDotRound, Share, User } from '@element-plus/icons-vue'
 import request from '../../api/request'
 
 const stats = ref([
   { label: '用户总数', value: 0, icon: 'UserFilled', bg: '#e6f7ff', color: '#1890ff' },
   { label: '课程总数', value: 0, icon: 'Notebook', bg: '#f0f9eb', color: '#67c23a' },
   { label: '问答总数', value: 0, icon: 'ChatDotRound', bg: '#fef0f0', color: '#f56c6c' },
   { label: '知识点数', value: 0, icon: 'Share', bg: '#fdf6ec', color: '#e6a23c' },
 ])
 
 onMounted(async () => {
   try {
     const res = await request.get('/api/admin/stats')
     if (res) {
       stats.value[0].value = res.users || 0
       stats.value[1].value = res.courses || 0
       stats.value[2].value = res.questions || 0
       stats.value[3].value = res.knowledge_points || 0
     }
   } catch { /* ignore */ }
 })
 </script>
 
 <style scoped>
 .ad-page { padding: 0; }
 .page-head { margin-bottom: 24px; }
 .page-title { font-size: 20px; font-weight: 600; color: #1d2129; margin: 0 0 4px; }
 .page-desc { font-size: 14px; color: #86909c; }
 .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 24px; }
 .stat-card { background: #fff; border-radius: 8px; padding: 24px; display: flex; align-items: center; gap: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
 .stat-icon { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; }
 .stat-value { font-size: 24px; font-weight: 700; color: #1d2129; line-height: 1.2; }
 .stat-label { font-size: 13px; color: #86909c; margin-top: 4px; }
 .manage-card { border-radius: 8px; text-align: center; padding: 12px 0; }
 .manage-card :deep(.el-card__header) { font-size: 15px; font-weight: 600; }
 </style>
