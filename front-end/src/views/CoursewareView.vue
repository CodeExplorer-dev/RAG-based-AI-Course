<template>
  <div class="cw-page">
    <div class="page-head">
      <h2 class="page-title">课件管理</h2>
      <el-select v-model="selectedCourseId" placeholder="请选择课程" @change="loadCourseware" style="width: 220px">
        <el-option
          v-for="c in courseList"
          :key="c.id"
          :label="c.course_name"
          :value="c.id"
        />
      </el-select>
    </div>

    <template v-if="selectedCourseId">
      <div v-if="isTeacher" class="upload-zone" @dragover.prevent @drop.prevent="handleDrop">
        <el-upload
          :http-request="uploadFile"
          :show-file-list="false"
          accept=".pdf,.ppt,.pptx,.doc,.docx,.txt,.md"
          class="upload-inner"
        >
          <div class="upload-content">
            <el-icon :size="36" color="#c0c4cc"><Upload /></el-icon>
            <p class="upload-text">点击或拖拽文件到此区域上传</p>
            <p class="upload-hint">支持 PDF、PPT、PPTX、DOC、DOCX、TXT、MD 格式</p>
          </div>
        </el-upload>
      </div>

      <div class="cw-table-wrap">
        <el-table :data="coursewareList" v-loading="loading" stripe>
          <el-table-column prop="title" label="文件名" min-width="200">
            <template #default="{ row }">
              <div class="file-cell">
                <el-icon :size="18" color="#409eff"><Document /></el-icon>
                <span>{{ row.title }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="file_type" label="类型" width="80" />
          <el-table-column label="大小" width="90">
            <template #default="{ row }">
              {{ formatSize(row.file_size) }}
            </template>
          </el-table-column>
          <el-table-column label="分块数" width="80">
            <template #default="{ row }">
              {{ row.chunk_count || 0 }}
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="110">
            <template #default="{ row }">
              <el-tag :type="statusTag(row.status)" size="small" round>
                {{ row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="上传时间" width="170">
            <template #default="{ row }">{{ formatTime(row.uploaded_at) }}</template>
          </el-table-column>
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
    </template>

    <el-empty v-else :image-size="120" description="请先选择一个课程" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, Document, Delete } from '@element-plus/icons-vue'
import { listCourses } from '../api/course'
import { listCourseware, uploadCourseware, deleteCourseware } from '../api/courseware'
import { formatTime } from '../utils/formatTime'
import { useUserStore } from '../stores/user'

const route = useRoute()
const userStore = useUserStore()
const isTeacher = computed(() => userStore.userInfo?.role === 'teacher')
const loading = ref(false)
const coursewareList = ref([])
const courseList = ref([])
const selectedCourseId = ref(null)

onMounted(async () => {
  // 加载用户课程列表供选择
  try {
    const res = await listCourses()
    courseList.value = res.data?.courses || []
  } catch { courseList.value = [] }

  // 如果 URL 带有 course_id 参数，自动选中
  const urlCourseId = route.query.course_id
  if (urlCourseId) {
    selectedCourseId.value = Number(urlCourseId)
    await loadCourseware()
  }
})

async function loadCourseware() {
  if (!selectedCourseId.value) return
  loading.value = true
  try {
    const res = await listCourseware(selectedCourseId.value)
    coursewareList.value = res.data?.courseware || []
  } catch { coursewareList.value = [] }
  loading.value = false
}

function handleDrop(e) {
  const file = e.dataTransfer.files[0]
  if (file) uploadFileCore(file)
}

async function uploadFile(options) {
  uploadFileCore(options.file)
}

async function uploadFileCore(file) {
  if (!selectedCourseId.value) {
    ElMessage.warning('请先选择课程')
    return
  }
  const formData = new FormData()
  formData.append('file', file)
  formData.append('course_id', selectedCourseId.value)
  try {
    await uploadCourseware(formData)
    ElMessage.success('上传成功')
    await loadCourseware()
  } catch { /* 错误已在拦截器中处理 */ }
}

function formatSize(bytes) {
  if (!bytes) return '0 B'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1048576).toFixed(1) + ' MB'
}

function statusTag(status) {
  const map = { 'uploading': 'info', 'processing': 'warning', 'completed': 'success', 'failed': 'danger' }
  return map[status] || 'info'
}

async function deleteCw(row) {
  try {
    await ElMessageBox.confirm('确定删除该课件吗？', '提示', { type: 'warning' })
    await deleteCourseware(row.id)
    ElMessage.success('删除成功')
    coursewareList.value = coursewareList.value.filter(c => c.id !== row.id)
  } catch { /* 取消或错误 */ }
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
</style>
