<template>
  <div class="ac-page">
    <div class="page-head"><h2 class="page-title">课程管理</h2><el-tag type="info" size="large" effect="plain" round>共 {{ courses.length }} 门</el-tag></div>
    <div class="table-wrap">
      <el-table :data="courses" v-loading="loading" stripe size="large">
        <el-table-column prop="course_name" label="课程名称" min-width="180">
          <template #default="{ row }"><div class="course-cell"><div class="course-icon"><el-icon :size="16"><Notebook /></el-icon></div><span>{{ row.course_name }}</span></div></template>
        </el-table-column>
        <el-table-column label="创建教师" width="140"><template #default="{ row }">{{ row.teacher?.username || '-' }}</template></el-table-column>
        <el-table-column prop="join_code" label="加入码" width="120" align="center"><template #default="{ row }"><el-tag size="small" effect="plain" type="warning">{{ row.join_code }}</el-tag></template></el-table-column>
        <el-table-column prop="student_count" label="学生数" width="80" align="center" />
        <el-table-column prop="courseware_count" label="课件数" width="80" align="center" />
        <el-table-column label="创建时间" width="170" align="center"><template #default="{ row }">{{ formatTime(row.created_at) }}</template></el-table-column>
        <el-table-column label="操作" width="100" align="center"><template #default="{ row }"><el-button text type="danger" size="small" @click="deleteCourseFn(row)">删除</el-button></template></el-table-column>
      </el-table>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Notebook } from '@element-plus/icons-vue'
import request from '../../api/request'
import { formatTime } from '../../utils/formatTime'
const loading = ref(false); const courses = ref([]); onMounted(loadCourses)
async function loadCourses() { loading.value = true; try { const res = await request.get('/api/admin/courses'); courses.value = res.data?.courses || [] } catch { courses.value = [] }; loading.value = false }
async function deleteCourseFn(row) { try { await ElMessageBox.confirm(`确定删除课程「${row.course_name}」吗？`, '提示', { type: 'warning' }); await request.delete(`/api/admin/courses/${row.id}`); ElMessage.success('已删除'); loadCourses() } catch {} }
</script>
<style scoped>
.ac-page { padding: 0; }
.page-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px;  position: relative; }
.page-title { font-size: 26px; font-weight: 700; color: var(--text-primary); margin: 0; letter-spacing: -0.5px; }
.page-title::after { content: ""; display: block; width: 36px; height: 3px; background: linear-gradient(90deg, #4a7cff, #7c5ce7); border-radius: 2px; margin-top: 8px; opacity: 0.4; }
.table-wrap { background: var(--bg-card); border-radius: var(--radius-lg); box-shadow: var(--shadow-sm); border: 1px solid var(--border-light); overflow: hidden; }
.course-cell { display: flex; align-items: center; gap: 8px; }
.course-icon { width: 28px; height: 28px; background: #ecf5ff; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: var(--primary); flex-shrink: 0; }
</style>


