<template>
  <div class="cw-page">
    <div class="page-head">
      <div class="page-head-left">
        <h2 class="page-title">课件管理</h2>
        <p class="page-subtitle">上传、查看和管理课程课件</p>
      </div>
      <el-select v-model="selectedCourseId" placeholder="请选择课程" @change="loadCourseware" style="width: 220px" clearable>
        <el-option v-for="c in courseList" :key="c.id" :label="c.course_name" :value="c.id" />
      </el-select>
    </div>
    <template v-if="selectedCourseId">
      <div v-if="isTeacher" class="upload-zone" @dragover.prevent @drop.prevent="handleDrop">
        <div class="upload-border"></div>
        <el-upload :http-request="uploadFile" :show-file-list="false" accept=".pdf,.ppt,.pptx,.doc,.docx,.txt,.md" class="upload-inner">
          <div class="upload-content">
            <div class="upload-icon-wrap">
              <el-icon :size="36" color="#5b8def"><UploadFilled /></el-icon>
            </div>
            <p class="upload-text">拖拽文件到此处上传，或<span class="upload-link">点击选择文件</span></p>
            <p class="upload-hint">支持 PDF、PPT、PPTX、DOC、DOCX、TXT、MD 格式</p>
          </div>
        </el-upload>
      </div>
      <div class="cw-table-wrap">
        <el-table :data="coursewareList" v-loading="loading" stripe size="large">
          <el-table-column prop="title" label="文件名" min-width="220">
            <template #default="{ row }">
              <div class="file-cell">
                <div class="file-icon" :class="getFileTypeClass(row.file_type)"><el-icon :size="18"><Document /></el-icon></div>
                <span class="file-name">{{ row.title }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="file_type" label="类型" width="80" align="center" />
          <el-table-column label="大小" width="100" align="center">
            <template #default="{ row }">{{ formatSize(row.file_size) }}</template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="120" align="center">
            <template #default="{ row }">
              <el-tag :type="statusTag(row.status)" size="small" round effect="dark">
                {{ row.status === 'completed' ? '已完成' : row.status === 'processing' ? '处理中' : row.status === 'failed' ? '失败' : '等待中' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="上传时间" width="170" align="center">
            <template #default="{ row }">{{ formatTime(row.uploaded_at) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="160" align="center">
            <template #default="{ row }">
              <el-button text type="primary" size="small" @click="viewChunks(row)">详情</el-button>
              <el-divider direction="vertical" />
              <el-popconfirm title="确定删除该课件吗？" @confirm="deleteCw(row)">
                <template #reference>
                  <el-button text type="danger" size="small">删除</el-button>
                </template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-if="!loading && !coursewareList.length" :image-size="80" description="暂无课件" />
      </div>
    </template>
    <div v-else class="empty-state">
      <div class="empty-graphic"><div class="empty-orb"></div><el-icon :size="48" color="#5b8def" class="empty-icon"><FolderOpened /></el-icon></div>
      <p class="empty-title">请先选择一个课程</p>
      <p class="empty-desc">选择课程后即可查看和管理课件</p>
    </div>
    <el-dialog v-model="chunkDialogVisible" class="chunk-dialog" :title="'解析详情 - ' + selectedCwTitle" width="750px" top="5vh" @close="chunksData=[]">
      <div v-loading="chunksLoading">
        <div v-if="!chunksLoading && chunksData.length === 0" style="text-align:center;padding:40px"><el-empty description="暂无解析数据 / 课件尚未处理完成" /></div>
        <div v-for="(group, gIdx) in groupedChunks" :key="gIdx" style="margin-bottom:16px">
          <h4 class="chunk-group-heading"><el-icon><FolderOpened /></el-icon> {{ group.heading }}</h4>
          <div v-for="chunk in group.chunks" :key="chunk.chunk_index" class="chunk-card">
            <div class="chunk-meta"><span class="chunk-index">#{{ chunk.chunk_index }}</span><el-tag size="small">{{ chunk.token_count }} tokens</el-tag><el-tag v-if="chunk.page_ref" size="small" type="info">第{{ chunk.page_ref }}页</el-tag></div>
            <el-collapse><el-collapse-item title="查看完整内容" name="1"><pre class="chunk-content-pre">{{ chunk.content }}</pre></el-collapse-item></el-collapse>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Upload, UploadFilled, Document, Delete, FolderOpened } from '@element-plus/icons-vue'
import { listCourses } from '../api/course'
import { listCourseware, uploadCourseware, deleteCourseware, getCoursewareChunks } from '../api/courseware'
import { formatTime } from '../utils/formatTime'
import { useUserStore } from '../stores/user'

const route = useRoute(); const userStore = useUserStore()
const isTeacher = computed(() => userStore.userInfo?.role === 'teacher')
const loading = ref(false); const coursewareList = ref([]); const courseList = ref([]); const selectedCourseId = ref(null)

onMounted(async () => { try { const res = await listCourses(); courseList.value = res.data?.courses || [] } catch { courseList.value = [] }; const urlCourseId = route.query.course_id; if (urlCourseId) { selectedCourseId.value = Number(urlCourseId); await loadCourseware() } })
async function loadCourseware() { if (!selectedCourseId.value) return; loading.value = true; try { const res = await listCourseware(selectedCourseId.value); coursewareList.value = res.data?.courseware || [] } catch { coursewareList.value = [] }; loading.value = false }
function handleDrop(e) { const file = e.dataTransfer.files[0]; if (file) uploadFileCore(file) }
async function uploadFile(options) { uploadFileCore(options.file) }
async function uploadFileCore(file) { if (!selectedCourseId.value) { ElMessage.warning('请先选择课程'); return }; const formData = new FormData(); formData.append('file', file); formData.append('course_id', selectedCourseId.value); try { await uploadCourseware(formData); ElMessage.success('上传成功'); await loadCourseware() } catch {} }
function getFileTypeClass(type) { return 'file-' + (type?.toLowerCase() || 'unknown') }
function formatSize(bytes) { if (!bytes) return '0 B'; if (bytes < 1024) return bytes + ' B'; if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB'; return (bytes / 1048576).toFixed(1) + ' MB' }
function statusTag(status) { const map = { uploading: 'info', processing: 'warning', completed: 'success', failed: 'danger' }; return map[status] || 'info' }
async function deleteCw(row) { try { await deleteCourseware(row.id); ElMessage.success('删除成功'); coursewareList.value = coursewareList.value.filter(c => c.id !== row.id) } catch {} }
const chunkDialogVisible = ref(false); const chunksLoading = ref(false); const chunksData = ref([]); const selectedCwTitle = ref('')
const groupedChunks = computed(() => { const groups = []; let cur = null; for (const chunk of chunksData.value) { const h = parseHeading(chunk.content); if (!cur || cur.heading !== h) { cur = { heading: h, chunks: [] }; groups.push(cur) }; cur.chunks.push(chunk) }; return groups })
function parseHeading(text) { const m = text.match(/^【([^】]+)】/); return m ? m[1] : '未分段' }
async function viewChunks(row) { selectedCwTitle.value = row.title; chunkDialogVisible.value = true; chunksLoading.value = true; chunksData.value = []; try { const res = await getCoursewareChunks(row.id); chunksData.value = (res.data?.chunks || []).filter(c => c.content) } catch { chunksData.value = [] }; chunksLoading.value = false }
</script>

<style scoped>
.cw-page { padding: 0; }
.page-head { display: flex; align-items: flex-end; justify-content: space-between; position: relative; margin-bottom: 24px; }
.page-head-left {}
.page-title { font-size: 26px; font-weight: 700; color: var(--text-primary); margin: 0; letter-spacing: -0.5px; }
.page-title::after { content: ""; display: block; width: 40px; height: 3px; background: linear-gradient(90deg, #52b859,#4a7cff); border-radius: 2px; margin-top: 8px; opacity: 0.5; }
.page-subtitle { font-size: 14px; color: var(--text-tertiary); margin-top: 4px; }

.upload-zone { position: relative;
  position: relative;
  background: linear-gradient(135deg, #f0f6ff 0%, #eaf1fe 100%);
  border-radius: 16px; margin-bottom: 24px; overflow: hidden;
  cursor: pointer; transition: all var(--transition-normal);
}
.upload-border {
  position: absolute; inset: 0; border-radius: 16px;
  border: 2px dashed rgba(91,141,239,0.3);
  transition: all var(--transition-normal);
  pointer-events: none;
}
.upload-zone:hover .upload-border { border-color: #409eff; border-width: 2px; }
.upload-zone:hover { box-shadow: 0 4px 20px rgba(64,158,255,0.08); }
.upload-inner { width: 100%; }
.upload-zone :deep(.el-upload) { display: flex; align-items: center; justify-content: center; width: 100%; min-height: 160px; }
.upload-content { padding: 28px 20px; text-align: center; position: relative; z-index: 1; }
.upload-icon-wrap { width: 60px; height: 60px; margin: 0 auto 14px; background: rgba(91,141,239,0.1); border-radius: 16px; display: flex; align-items: center; justify-content: center; }
.upload-text { font-size: 16px; color: var(--text-primary); margin: 0 0 8px; }
.upload-link { color: var(--primary); font-weight: 500; cursor: pointer; }
.upload-hint { font-size: 13px; color: var(--text-tertiary); margin: 0; }

.cw-deco { height: 3px; background: linear-gradient(90deg, #52b859, #4a7cff); border-radius: 2px; margin-bottom: 0; opacity: 0.5; }
.cw-table-wrap { background: var(--bg-card-gradient); border-radius: var(--radius-lg); box-shadow: var(--shadow-sm); border: 1px solid var(--border-light); overflow: hidden; }
.file-cell { display: flex; align-items: center; gap: 10px; }
.file-icon { width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.file-icon { background: #ecf5ff; color: var(--primary); }
.file-name { font-weight: 500; color: var(--text-primary); }

.empty-state { text-align: center; padding: 80px 20px; }
.empty-graphic { position: relative; width: 100px; height: 100px; margin: 0 auto 24px; display: flex; align-items: center; justify-content: center; }
.empty-orb { position: absolute; width: 100%; height: 100%; border-radius: 50%; background: radial-gradient(circle at 30% 30%, #e8f4fd, #d0e8ff); opacity: 0.4; animation: orb-pulse 4s ease-in-out infinite; }
@keyframes orb-pulse { 0%,100% { transform: scale(1); opacity: 0.4; } 50% { transform: scale(1.1); opacity: 0.6; } }
.empty-icon { position: relative; z-index: 1; }
.empty-title { font-size: 20px; font-weight: 600; color: var(--text-primary); margin: 0 0 8px; }
.empty-desc { font-size: 15px; color: var(--text-tertiary); margin: 0; }

.chunk-group-heading { margin: 0 0 10px; font-size: 15px; color: var(--text-primary); font-weight: 600; display: flex; align-items: center; gap: 6px; }
.chunk-card { background: #fafafa; border: 1px solid var(--border-light); border-radius: 8px; padding: 12px 16px; margin-bottom: 8px; transition: all var(--transition-fast); }
.chunk-card:hover { border-color: #d0d7e0; }
.chunk-meta { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.chunk-index { font-weight: 600; color: var(--primary); font-size: 13px; }
.chunk-content-pre { white-space: pre-wrap; word-break: break-all; font-size: 13px; line-height: 1.7; max-height: 300px; overflow-y: auto; background: var(--bg-card-gradient); padding: 12px; border-radius: 6px; color: var(--text-secondary); }
</style>



