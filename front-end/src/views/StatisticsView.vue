 <template>
   <div class="stats-page">
     <div class="page-head">
       <h2 class="page-title">提问统计</h2>
     </div>
     <div class="stats-grid">
       <div class="stat-card">
         <div class="stat-icon" style="background: #e6f7ff;">
           <el-icon :size="24" color="#1890ff"><ChatDotRound /></el-icon>
         </div>
         <div class="stat-body">
           <div class="stat-value">{{ stats.total_questions || 0 }}</div>
           <div class="stat-label">提问总数</div>
         </div>
       </div>
       <div class="stat-card">
         <div class="stat-icon" style="background: #f0f9eb;">
           <el-icon :size="24" color="#67c23a"><Reading /></el-icon>
         </div>
         <div class="stat-body">
           <div class="stat-value">{{ stats.total_courses || 0 }}</div>
           <div class="stat-label">覆盖课程</div>
         </div>
       </div>
       <div class="stat-card">
         <div class="stat-icon" style="background: #fef0f0;">
           <el-icon :size="24" color="#f56c6c"><Share /></el-icon>
         </div>
         <div class="stat-body">
           <div class="stat-value">{{ stats.total_knowledge_points || 0 }}</div>
           <div class="stat-label">知识点数</div>
         </div>
       </div>
     </div>
     <div class="rank-section">
       <h3 class="rank-title">高频问题排行</h3>
       <div v-if="stats.top_questions?.length" class="rank-list">
         <div v-for="(q, i) in stats.top_questions" :key="i" class="rank-item">
           <span :class="['rank-badge', i < 3 ? 'top' : '']">{{ i + 1 }}</span>
           <span class="rank-text">{{ q.text || q.question }}</span>
           <span class="rank-count">{{ q.count }} 次</span>
         </div>
       </div>
       <el-empty v-else :image-size="80" description="暂无高频问题数据" />
     </div>
   </div>
 </template>
 
 <script setup>
 import { ref, onMounted } from 'vue'
 import { ChatDotRound, Reading, Share } from '@element-plus/icons-vue'
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
 .page-head {
   display: flex;
   align-items: center;
   justify-content: space-between;
   margin-bottom: 24px;
 }
 .page-title { font-size: 20px; font-weight: 600; color: #1d2129; margin: 0; }
 .stats-grid {
   display: grid;
   grid-template-columns: repeat(3, 1fr);
   gap: 20px;
   margin-bottom: 24px;
 }
 .stat-card {
   background: #fff;
   border-radius: 8px;
   padding: 24px;
   display: flex;
   align-items: center;
   gap: 20px;
   box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
   transition: box-shadow 0.2s;
 }
 .stat-card:hover { box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08); }
 .stat-icon {
   width: 52px;
   height: 52px;
   border-radius: 12px;
   display: flex;
   align-items: center;
   justify-content: center;
   flex-shrink: 0;
 }
 .stat-value { font-size: 28px; font-weight: 700; color: #1d2129; line-height: 1.2; }
 .stat-label { font-size: 13px; color: #86909c; margin-top: 4px; }
 .rank-section {
   background: linear-gradient(135deg, #fff 0%, #fafcff 100%);
   border-radius: 8px;
   padding: 24px;
   box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
   border: 1px solid rgba(91,141,239,0.08);
 }
 .rank-title { font-size: 16px; font-weight: 600; color: #1d2129; margin: 0 0 16px; }
 .rank-list { margin: 0; }
 .rank-item {
   display: flex;
   align-items: center;
   padding: 12px 0;
   border-bottom: 1px solid #f0f0f5;
 }
 .rank-item:last-child { border-bottom: none; }
 .rank-badge {
   width: 24px;
   height: 24px;
   border-radius: 6px;
   background: #f5f7fa;
   display: flex;
   align-items: center;
   justify-content: center;
   font-size: 12px;
   font-weight: 600;
   color: #86909c;
   margin-right: 12px;
   flex-shrink: 0;
 }
 .rank-badge.top {
   background: #e6a23c;
   color: #fff;
 }
 .rank-item:nth-child(2) .rank-badge.top { background: #909399; }
 .rank-item:nth-child(3) .rank-badge.top { background: #cd7f32; }
 .rank-text { flex: 1; font-size: 14px; color: #1d2129; }
 .rank-count { font-size: 13px; color: #86909c; flex-shrink: 0; }
 </style>
