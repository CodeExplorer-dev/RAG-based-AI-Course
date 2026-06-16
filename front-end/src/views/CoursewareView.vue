 <template>
   <div class="courseware-page">
     <h2 class="page-title">课件管理</h2>
     <div class="cw-toolbar">
       <el-upload
         :http-request="uploadFile"
         :show-file-list="false"
         accept=".pdf,.ppt,.pptx,.doc,.docx"
       >
         <el-button type="primary">上传课件</el-button>
       </el-upload>
       <span class="cw-hint">支持 PDF、PPT、PPTX、DOC、DOCX 格式</span>
     </div>
     <el-table :data="coursewareList" style="width: 100%" v-loading="loading">
       <el-table-column prop="name" label="文件名" />
       <el-table-column prop="course_name" label="所属课程" />
       <el-table-column prop="size" label="大小" width="100" />
       <el-table-column prop="status" label="解析状态" width="120">
         <template #default="{ row }">
           <el-tag :type="statusTag(row.status)">{{ row.status }}</el-tag>
         </template>
       </el-table-column>
       <el-table-column prop="created_at" label="上传时间" width="180" />
       <el-table-column label="操作" width="120">
         <template #default="{ row }">
           <el-button text type="danger" @click="deleteCw(row)">删除</el-button>
         </template>
       </el-table-column>
     </el-table>
     <el-empty v-if="!loading && !coursewareList.length" description="暂无课件，请上传" />
   </div>
 </template>
 
 <script setup>
 import { ref, onMounted } from 'vue'
 import { ElMessage, ElMessageBox } from 'element-plus'
 import request from '../api/request'
 
 const loading = ref(false)
 const coursewareList = ref([])
 
 onMounted(async () => {
   loading.value = true
   try {
     const res = await request.get('/api/courseware')
     coursewareList.value = res.courseware || []
   } catch { /* ignore */ }
   loading.value = false
 })
 
 async function uploadFile(options) {
   const formData = new FormData()
   formData.append('file', options.file)
   try {
     await request.post('/api/courseware/upload', formData, {
       headers: { 'Content-Type': 'multipart/form-data' }
     })
     ElMessage.success('上传成功，正在解析')
     onMounted()
   } catch { /* ignore */ }
 }
 
 function statusTag(status) {
   const map = { '处理中': 'warning', '已完成': 'success', '失败': 'danger' }
   return map[status] || 'info'
 }
 
 async function deleteCw(row) {
   try {
     await ElMessageBox.confirm('确定删除该课件吗？', '提示')
     await request.delete(`/api/courseware/${row.id}`)
     ElMessage.success('删除成功')
     coursewareList.value = coursewareList.value.filter(c => c.id !== row.id)
   } catch { /* ignore */ }
 }
 </script>
 
 <style scoped>
 .courseware-page { padding: 0; }
 .page-title { font-size: 20px; margin-bottom: 20px; color: #303133; }
 .cw-toolbar { display: flex; align-items: center; gap: 16px; margin-bottom: 16px; }
 .cw-hint { font-size: 12px; color: #909399; }
 </style>
