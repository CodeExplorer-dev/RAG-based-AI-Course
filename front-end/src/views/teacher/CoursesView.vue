<template>
  <div class="tc-page">
    <div class="page-head"><h2 class="page-title">课程管理</h2><el-button type="primary" :icon="Plus" size="large" round @click="showCreate = true">创建课程</el-button></div>
    <div class="table-wrap">
      <el-table :data="courses" v-loading="loading" stripe size="large">
        <el-table-column prop="course_name" label="课程名称" min-width="200">
          <template #default="{ row }"><div class="course-cell"><div class="course-icon"><el-icon :size="16"><Notebook /></el-icon></div><span>{{ row.course_name }}</span></div></template>
        </el-table-column>
        <el-table-column prop="join_code" label="加入码" width="140" align="center"><template #default="{ row }"><el-tag type="warning" effect="dark">{{ row.join_code }}</el-tag></template></el-table-column>
        <el-table-column prop="student_count" label="学生人数" width="100" align="center" />
        <el-table-column label="创建时间" width="170" align="center"><template #default="{ row }">{{ formatTime(row.created_at) }}</template></el-table-column>
        <el-table-column label="操作" width="220" align="center">
          <template #default="{ row }">
            <el-button text type="primary" size="small" @click="copyCode(row.join_code)">复制加入码</el-button>
            <el-divider direction="vertical" />
            <el-button text type="danger" size="small" @click="deleteCourseFn(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && !courses.length" :image-size="80" description="还没有创建课程" />
    </div>
    <el-dialog v-model="showCreate" title="创建课程" width="460px" :close-on-click-modal="false" top="25vh">
      <el-form :model="form" label-width="80px"><el-form-item label="课程名称" required><el-input v-model="form.course_name" placeholder="请输入课程名称" size="large" /></el-form-item><el-form-item label="课程描述"><el-input v-model="form.description" type="textarea" :rows="3" placeholder="可选" /></el-form-item></el-form>
      <template #footer><el-button @click="showCreate = false">取消</el-button><el-button type="primary" :loading="saving" @click="handleCreate">创建</el-button></template>
    </el-dialog>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Notebook } from '@element-plus/icons-vue'
import { listCourses, createCourse, deleteCourse } from '../../api/course'
import { formatTime } from '../../utils/formatTime'
const loading = ref(false); const saving = ref(false); const courses = ref([]); const showCreate = ref(false); const form = ref({ course_name: '', description: '' }); onMounted(loadMyCourses)
async function loadMyCourses() { loading.value = true; try { const res = await listCourses(); courses.value = (res.data?.courses || []).filter(c => c.role === 'teacher') } catch { courses.value = [] }; loading.value = false }
async function handleCreate() { if (!form.value.course_name) { ElMessage.warning('请输入课程名称'); return }; saving.value = true; try { await createCourse({ course_name: form.value.course_name, description: form.value.description }); ElMessage.success('创建成功'); showCreate.value = false; form.value = { course_name: '', description: '' }; loadMyCourses() } finally { saving.value = false } }
function copyCode(code) { navigator.clipboard.writeText(code); ElMessage.success('已复制加入码：' + code) }
async function deleteCourseFn(row) { try { await ElMessageBox.confirm(`确定删除课程「${row.course_name}」吗？`, '提示', { type: 'warning' }); await deleteCourse(row.id); ElMessage.success('删除成功'); loadMyCourses() } catch {} }
</script>
<style scoped>
.tc-page { padding: 0; }
.page-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px;  position: relative; }
.page-title { font-size: 26px; font-weight: 700; color: var(--text-primary); margin: 0; letter-spacing: -0.5px; }
.page-title::after { content: ""; display: block; width: 36px; height: 3px; background: linear-gradient(90deg, #4a7cff, #7c5ce7); border-radius: 2px; margin-top: 8px; opacity: 0.4; }
.table-wrap { background: var(--bg-card); border-radius: var(--radius-lg); box-shadow: var(--shadow-sm); border: 1px solid var(--border-light); overflow: hidden; }
.course-cell { display: flex; align-items: center; gap: 8px; }
.course-icon { width: 28px; height: 28px; background: #ecf5ff; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: var(--primary); flex-shrink: 0; }
</style>


