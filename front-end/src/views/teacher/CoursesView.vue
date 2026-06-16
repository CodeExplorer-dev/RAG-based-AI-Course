 <template>
   <div class="tc-page">
     <div class="page-head">
       <h2 class="page-title">课程管理</h2>
       <el-button type="primary" :icon="Plus" @click="showCreate = true">创建课程</el-button>
     </div>
     <el-table :data="courses" v-loading="loading" stripe>
       <el-table-column prop="name" label="课程名称" min-width="180" />
       <el-table-column prop="code" label="加入码" width="140">
         <template #default="{ row }">
           <el-tag type="warning" effect="plain">{{ row.code }}</el-tag>
         </template>
       </el-table-column>
       <el-table-column prop="student_count" label="学生人数" width="100" align="center" />
       <el-table-column prop="created_at" label="创建时间" width="170" />
       <el-table-column label="操作" width="140" align="center">
         <template #default="{ row }">
           <el-button text type="primary" size="small" @click="copyCode(row.code)">复制加入码</el-button>
           <el-button text type="danger" size="small" @click="deleteCourse(row)">删除</el-button>
         </template>
       </el-table-column>
     </el-table>
     <el-empty v-if="!loading && !courses.length" :image-size="80" description="还没有创建课程" />
 
     <el-dialog v-model="showCreate" title="创建课程" width="460px" :close-on-click-modal="false">
       <el-form :model="form" label-width="80px">
         <el-form-item label="课程名称" required>
           <el-input v-model="form.name" placeholder="请输入课程名称" />
         </el-form-item>
         <el-form-item label="课程描述">
           <el-input v-model="form.description" type="textarea" :rows="3" placeholder="可选" />
         </el-form-item>
         <el-form-item label="加入码">
           <el-input v-model="form.code" placeholder="留空自动生成" />
         </el-form-item>
       </el-form>
       <template #footer>
         <el-button @click="showCreate = false">取消</el-button>
         <el-button type="primary" :loading="saving" @click="createCourse">创建</el-button>
       </template>
     </el-dialog>
   </div>
 </template>
 
 <script setup>
 import { ref, onMounted } from 'vue'
 import { ElMessage, ElMessageBox } from 'element-plus'
 import { Plus } from '@element-plus/icons-vue'
 import request from '../../api/request'
 
 const loading = ref(false)
 const saving = ref(false)
 const courses = ref([])
 const showCreate = ref(false)
 const form = ref({ name: '', description: '', code: '' })
 
 onMounted(loadCourses)
 
 async function loadCourses() {
   loading.value = true
   try {
     const res = await request.get('/api/teacher/courses')
     courses.value = res.courses || []
   } catch { courses.value = [] }
   loading.value = false
 }
 
 async function createCourse() {
   if (!form.value.name) { ElMessage.warning('请输入课程名称'); return }
   saving.value = true
   try {
     await request.post('/api/teacher/courses', form.value)
     ElMessage.success('创建成功')
     showCreate.value = false
     form.value = { name: '', description: '', code: '' }
     loadCourses()
   } finally { saving.value = false }
 }
 
 function copyCode(code) {
   navigator.clipboard.writeText(code)
   ElMessage.success('已复制加入码：' + code)
 }
 
 async function deleteCourse(row) {
   try {
     await ElMessageBox.confirm('确定删除课程「' + row.name + '」吗？', '提示', { type: 'warning' })
     await request.delete('/api/teacher/courses/' + row.id)
     ElMessage.success('删除成功')
     loadCourses()
   } catch { /* ignore */ }
 }
 </script>
 
 <style scoped>
 .tc-page { padding: 0; }
 .page-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
 .page-title { font-size: 20px; font-weight: 600; color: #1d2129; margin: 0; }
 </style>
