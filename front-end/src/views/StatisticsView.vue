 <template>
   <div class="stats-page">
     <h2 class="page-title">提问统计</h2>
     <el-row :gutter="20" class="stats-cards">
       <el-col :span="8">
         <el-card shadow="hover">
           <div class="stat-item">
             <div class="stat-value">{{ stats.total_questions || 0 }}</div>
             <div class="stat-label">提问总数</div>
           </div>
         </el-card>
       </el-col>
       <el-col :span="8">
         <el-card shadow="hover">
           <div class="stat-item">
             <div class="stat-value">{{ stats.total_courses || 0 }}</div>
             <div class="stat-label">覆盖课程</div>
           </div>
         </el-card>
       </el-col>
       <el-col :span="8">
         <el-card shadow="hover">
           <div class="stat-item">
             <div class="stat-value">{{ stats.total_knowledge_points || 0 }}</div>
             <div class="stat-label">知识点数</div>
           </div>
         </el-card>
       </el-col>
     </el-row>
     <el-card class="stats-card" title="高频问题排行">
       <div v-if="stats.top_questions?.length">
         <div v-for="(q, i) in stats.top_questions" :key="i" class="rank-item">
           <span class="rank-num">{{ i + 1 }}</span>
           <span class="rank-text">{{ q.text || q.question }}</span>
           <span class="rank-count">{{ q.count }}次</span>
         </div>
       </div>
       <el-empty v-else description="暂无数据" />
     </el-card>
   </div>
 </template>
 
 <script setup>
 import { ref, onMounted } from 'vue'
 import request from '../api/request'
 
 const stats = ref({})
 
 onMounted(async () => {
   try {
     const res = await request.get('/api/statistics')
     stats.value = res
   } catch { /* ignore */ }
 })
 </script>
 
 <style scoped>
 .stats-page { padding: 0; }
 .page-title { font-size: 20px; margin-bottom: 20px; color: #303133; }
 .stats-cards { margin-bottom: 20px; }
 .stat-item { text-align: center; padding: 16px 0; }
 .stat-value { font-size: 36px; font-weight: 600; color: #409eff; }
 .stat-label { font-size: 14px; color: #909399; margin-top: 8px; }
 .stats-card { margin-top: 0; }
 .rank-item { display: flex; align-items: center; padding: 10px 0; border-bottom: 1px solid #f0f0f0; }
 .rank-item:last-child { border-bottom: none; }
 .rank-num { width: 28px; height: 28px; border-radius: 50%; background: #f0f2f5; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 600; margin-right: 12px; }
 .rank-item:nth-child(1) .rank-num { background: #e6a23c; color: #fff; }
 .rank-item:nth-child(2) .rank-num { background: #909399; color: #fff; }
 .rank-item:nth-child(3) .rank-num { background: #cd7f32; color: #fff; }
 .rank-text { flex: 1; font-size: 14px; }
 .rank-count { font-size: 13px; color: #909399; margin-left: 12px; }
 </style>
