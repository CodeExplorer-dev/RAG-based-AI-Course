 <template>
   <div class="kg-page">
     <h2 class="page-title">知识图谱</h2>
     <div class="kg-toolbar">
       <el-select v-model="selectedCourse" placeholder="选择课程" @change="loadGraph">
         <el-option v-for="c in courses" :key="c.id" :label="c.name" :value="c.id" />
       </el-select>
       <el-button type="primary" @click="loadGraph">刷新图谱</el-button>
     </div>
     <el-card class="kg-card">
       <div ref="graphRef" class="kg-canvas">
         <el-empty v-if="!nodes.length" description="暂无知识图谱数据，请先上传课件" />
       </div>
     </el-card>
   </div>
 </template>
 
 <script setup>
 import { ref, onMounted } from 'vue'
 import request from '../api/request'
 
 const selectedCourse = ref('')
 const courses = ref([])
 const nodes = ref([])
 const edges = ref([])
 const graphRef = ref(null)
 
 onMounted(async () => {
   try {
     const res = await request.get('/api/courses')
     courses.value = res.courses || []
   } catch { /* ignore */ }
 })
 
 async function loadGraph() {
   if (!selectedCourse.value) return
   try {
     const res = await request.get(`/api/knowledge-graph/${selectedCourse.value}`)
     nodes.value = res.nodes || []
     edges.value = res.edges || []
   } catch {
     nodes.value = []
     edges.value = []
   }
   // d3.js / vis.js 渲染将在后续迭代中接入
 }
 </script>
 
 <style scoped>
 .kg-page { padding: 0; }
 .page-title { font-size: 20px; margin-bottom: 20px; color: #303133; }
 .kg-toolbar { display: flex; gap: 12px; margin-bottom: 16px; }
 .kg-card { min-height: 500px; }
 .kg-canvas { width: 100%; height: 500px; display: flex; align-items: center; justify-content: center; }
 </style>
