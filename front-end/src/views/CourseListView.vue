 <template>
   <div class="course-list-page">
     <h2 class="page-title">课程列表</h2>
     <el-row :gutter="20">
       <el-col v-for="course in courses" :key="course.id" :xs="24" :sm="12" :md="8" :lg="6" class="course-card-col">
         <el-card class="course-card" shadow="hover" @click="enterCourse(course)">
           <div class="course-icon">
             <el-icon :size="40" color="#409eff"><Reading /></el-icon>
           </div>
           <h3 class="course-name">{{ course.name }}</h3>
           <p class="course-desc">{{ course.description || course.teacher || course.id }}</p>
           <div class="course-meta">
             <el-tag size="small" type="info">{{ course.code || '无加入码' }}</el-tag>
           </div>
         </el-card>
       </el-col>
     </el-row>
     <el-empty v-if="!courses.length" description="暂无课程，联系教师获取加入码" />
   </div>
 </template>
 
 <script setup>
 import { ref, onMounted } from 'vue'
 import { useRouter } from 'vue-router'
 import { ElMessage } from 'element-plus'
 import { Reading } from '@element-plus/icons-vue'
 import request from '../api/request'
 
 const router = useRouter()
 const courses = ref([])
 
 onMounted(async () => {
   try {
     const res = await request.get('/api/courses')
     courses.value = res.courses || []
   } catch {
     courses.value = []
   }
 })
 
 function enterCourse(course) {
   router.push(`/chat/${course.id}`)
 }
 </script>
 
 <style scoped>
 .course-list-page { padding: 0; }
 .page-title { font-size: 20px; margin-bottom: 20px; color: #303133; }
 .course-card-col { margin-bottom: 20px; }
 .course-card { cursor: pointer; transition: transform 0.2s; }
 .course-card:hover { transform: translateY(-4px); }
 .course-icon { text-align: center; margin-bottom: 12px; }
 .course-name { font-size: 16px; text-align: center; margin: 0 0 8px; }
 .course-desc { font-size: 13px; color: #909399; text-align: center; margin: 0 0 12px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
 .course-meta { text-align: center; }
 </style>
