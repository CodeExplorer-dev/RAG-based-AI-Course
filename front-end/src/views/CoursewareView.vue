 <template>
   <div class="cw-page">
     <div class="page-head">
       <h2 class="page-title">课件管理</h2>
     </div>
     <div class="upload-zone" @dragover.prevent @drop.prevent="handleDrop">
       <el-upload
         :http-request="uploadFile"
         :show-file-list="false"
         accept=".pdf,.ppt,.pptx,.doc,.docx"
         class="upload-inner"
       >
         <div class="upload-content">
           <el-icon :size="36" color="#c0c4cc"><Upload /></el-icon>
           <p class="upload-text">点击或拖拽文件到此区域上传</p>
           <p class="upload-hint">支持 PDF、PPT、PPTX、DOC、DOCX 格式</p>
         </div>
       </el-upload>
     </div>
     <div class="cw-table-wrap">
       <el-table :data="coursewareList" v-loading="loading" stripe>
         <el-table-column prop="name" label="文件名" min-width="200">
           <template #default="{ row }">
             <div class="file-cell">
               <el-icon :size="18" color="#409eff"><Document /></el-icon>
               <span>{{ row.name }}</span>
             </div>
           </template>
         </el-table-column>
         <el-table-column prop="course_name" label="所属课程" width="140" />
         <el-table-column prop="size" label="大小" width="90" />
         <el-table-column prop="status" label="解析状态" width="110">
           <template #default="{ row }">
             <el-tag :type="statusTag(row.status)" size="small" round>
               <el-icon v-if="row.status === '处理中'" class="loading-icon" style="margin-right:4px"><Refresh /></el-icon>
               {{ row.status }}
             </el-tag>
           </template>
         </el-table-column>
         <el-table-column prop="created_at" label="上传时间" width="170" />
         <el-table-column label="操作" width="80" align="center">
           <template #default="{ row }">
             <el-tooltip content="删除" placement="top">
               <el-button text type="danger" :icon="Delete" circle @click="deleteCw(row)" />
             </el-tooltip>
           </template>
         </el-table-column>
       </el-table>
       <el-empty v-if="!loading && !coursewareList.length" :image-size="80" description="暂无课件" />
     </div>
   </div>
 </template>
 
 <script setup>
 import { ref, onMounted } from 'vue'
 import { ElMessage, ElMessageBox } from 'element-plus'
 import { Upload, Document, Delete, Refresh } from '@element-plus/icons-vue'
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
 
 function handleDrop(e) {
   const file = e.dataTransfer.files[0]
   if (file) uploadFileCore(file)
 }
 
 async function uploadFile(options) {
   uploadFileCore(options.file)
 }
 
 async function uploadFileCore(file) {
   const formData = new FormData()
   formData.append('file', file)
   try {
     await request.post('/api/courseware/upload', formData, {
       headers: { 'Content-Type': 'multipart/form-data' }
     })
     ElMessage.success('上传成功，正在解析')
     onMounted()
   } catch { /* ignore */ }
 }
 
 function statusTag(status) {
   return { '处理中': 'warning', '已完成': 'success', '失败': 'danger' }[status] || 'info'
 }
 
 async function deleteCw(row) {
   try {
     await ElMessageBox.confirm('确定删除该课件吗？', '提示', { type: 'warning' })
     await request.delete(`/api/courseware/${row.id}`)
     ElMessage.success('删除成功')
     coursewareList.value = coursewareList.value.filter(c => c.id !== row.id)
   } catch { /* ignore */ }
 }
 </script>
 
 <style scoped>
 .cw-page { padding: 0; }
 .page-head {
   display: flex;
   align-items: center;
   justify-content: space-between;
   margin-bottom: 20px;
 }
 .page-title { font-size: 26px; font-weight: 600; color: #1d2129; margin: 0; }
 .upload-zone {
   background: linear-gradient(135deg, #fafcff 0%, #f0f4ff 100%);
   border: 2px dashed rgba(91,141,239,0.25);
   border-radius: 8px;
   margin-bottom: 20px;
   transition: border-color 0.2s, background 0.2s;
   cursor: pointer;
 }
 .upload-zone .upload-text { color: #5b8def; }
 .upload-zone .upload-hint { color: #86909c; }
 .upload-zone:hover {
   border-color: #409eff;
   background: #f0f9ff;
 }
 .upload-inner { width: 100%; }
.upload-zone :deep(.el-upload) {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  min-height: 180px;
}
 .upload-content {
   padding: 32px 20px;
   text-align: center;
 }
 .upload-text { font-size: 18px; color: #1d2129; margin: 12px 0 4px; text-align: center; }
 .upload-hint { font-size: 16px; color: #86909c; margin: 0; text-align: center; }
 .cw-table-wrap { background: #fff; border-radius: 8px; }
 .file-cell { display: flex; align-items: center; gap: 8px; }
 .loading-icon { animation: spin 1s linear infinite; }
 @keyframes spin { to { transform: rotate(360deg); } }
 </style>
