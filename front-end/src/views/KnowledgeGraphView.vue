 <template>
   <div class="kg-page">
     <div class="page-head">
       <h2 class="page-title">知识图谱</h2>
       <div class="kg-actions">
         <el-select v-model="selectedCourse" placeholder="选择课程" size="default" @change="loadGraph">
           <el-option v-for="c in courses" :key="c.id" :label="c.name" :value="c.id" />
         </el-select>
         <el-button type="primary" :icon="Refresh" :disabled="!selectedCourse" @click="loadGraph" />
       </div>
     </div>
     <div class="kg-canvas" ref="graphRef">
       <div v-if="!nodes.length && !loading" class="empty-state">
         <el-icon :size="64" color="#d0d5dd"><Share /></el-icon>
         <p class="empty-title">知识图谱</p>
         <p class="empty-desc">选择课程后，系统将自动从课件中提取知识点并构建关联图谱</p>
       </div>
       <div v-if="loading" class="loading-state">
         <el-icon class="loading-spin" :size="32" color="#409eff"><Refresh /></el-icon>
         <p>正在生成图谱...</p>
       </div>
     </div>
   </div>
 </template>
 
 <script setup>
 import { ref, onMounted } from 'vue'
 import { Refresh, Share } from '@element-plus/icons-vue'
 import request from '../api/request'
 
 const selectedCourse = ref('')
 const courses = ref([])
 const nodes = ref([])
 const edges = ref([])
 const loading = ref(false)
 const graphRef = ref(null)
 
 onMounted(async () => {
   try {
     const res = await request.get('/api/courses')
     courses.value = res.courses || []
   } catch { /* ignore */ }
 })
 
 async function loadGraph() {
   if (!selectedCourse.value) return
   loading.value = true
   try {
     const res = await request.get(`/api/knowledge-graph/${selectedCourse.value}`)
     nodes.value = res.nodes || []
     edges.value = res.edges || []
   } catch {
     nodes.value = []
     edges.value = []
   }
   loading.value = false
 }
 </script>
 
 <style scoped>
 .kg-page { padding: 0; }
 .page-head {
   display: flex;
   align-items: center;
   justify-content: space-between;
   margin-bottom: 20px;
 }
 .page-title { font-size: 20px; font-weight: 600; color: #1d2129; margin: 0; }
 .kg-actions { display: flex; gap: 8px; }
 .kg-canvas {
   background: linear-gradient(135deg, #f8faff 0%, #f0f4ff 50%, #fdf2f8 100%);
   border-radius: 8px;
   min-height: 520px;
   display: flex;
   align-items: center;
   justify-content: center;
   border: 1px solid rgba(91,141,239,0.12);
   background-image:
     radial-gradient(circle, rgba(91,141,239,0.08) 1px, transparent 1px);
   background-size: 24px 24px;
 }
 .empty-state {
   text-align: center;
   padding: 60px 40px;
 }
 .empty-title { font-size: 18px; font-weight: 600; color: #1d2129; margin: 16px 0 6px; }
 .empty-desc { font-size: 14px; color: #86909c; margin: 0; max-width: 360px; }
 .loading-state {
   text-align: center;
   color: #86909c;
 }
 .loading-spin { animation: spin 1s linear infinite; }
 @keyframes spin { to { transform: rotate(360deg); } }
 </style>
