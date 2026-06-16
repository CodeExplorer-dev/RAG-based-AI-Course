 <template>
   <div class="lp-page">
     <h2 class="page-title">学习路径推荐</h2>
     <div class="lp-toolbar">
       <el-select v-model="selectedCourse" placeholder="选择课程">
         <el-option v-for="c in courses" :key="c.id" :label="c.name" :value="c.id" />
       </el-select>
       <el-button type="primary" :disabled="!selectedCourse" @click="loadPath">生成推荐</el-button>
     </div>
     <el-card v-if="pathSteps.length" class="lp-card">
       <el-steps direction="vertical" :active="currentStep" finish-status="success">
         <el-step v-for="(step, i) in pathSteps" :key="i" :title="step.name" :description="step.description" />
       </el-steps>
     </el-card>
     <el-empty v-else description="选择课程并生成学习路径" />
   </div>
 </template>
 
 <script setup>
 import { ref, onMounted } from 'vue'
 import request from '../api/request'
 
 const selectedCourse = ref('')
 const courses = ref([])
 const pathSteps = ref([])
 const currentStep = ref(-1)
 
 onMounted(async () => {
   try {
     const res = await request.get('/api/courses')
     courses.value = res.courses || []
   } catch { /* ignore */ }
 })
 
 async function loadPath() {
   if (!selectedCourse.value) return
   try {
     const res = await request.get(`/api/learning-path/${selectedCourse.value}`)
     pathSteps.value = res.steps || []
   } catch {
     pathSteps.value = []
   }
 }
 </script>
 
 <style scoped>
 .lp-page { padding: 0; }
 .page-title { font-size: 20px; margin-bottom: 20px; color: #303133; }
 .lp-toolbar { display: flex; gap: 12px; margin-bottom: 16px; }
 .lp-card { padding: 24px; }
 </style>
