<template>
  <div class="ac-page">
    <div class="page-head">
      <h2 class="page-title">课程管理</h2>
      <el-tag type="info">共 {{ courses.length }} 门</el-tag>
    </div>
    <el-table :data="courses" v-loading="loading" stripe>
      <el-table-column prop="course_name" label="课程名称" min-width="180" />
      <el-table-column label="创建教师" width="140">
        <template #default="{ row }">
          {{ row.teacher?.username || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="join_code" label="加入码" width="120">
        <template #default="{ row }"><el-tag size="small">{{ row.join_code }}</el-tag></template>
      </el-table-column>
      <el-table-column prop="student_count" label="学生数" width="80" align="center" />
      <el-table-column prop="courseware_count" label="课件数" width="80" align="center" />
      <el-table-column prop="created_at" label="创建时间" width="170" />
      <el-table-column label="操作" width="80" align="center">
        <template #default="{ row }">
          <el-button text type="danger" size="small" @click="deleteCourseFn(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '../../api/request'

const loading = ref(false)
const courses = ref([])

onMounted(loadCourses)

async function loadCourses() {
  loading.value = true
  try {
    const res = await request.get('/api/admin/courses')
    courses.value = res.data?.courses || []
  } catch { courses.value = [] }
  loading.value = false
}

async function deleteCourseFn(row) {
  try {
    await ElMessageBox.confirm(`确定删除课程「${row.course_name}」吗？`, '提示', { type: 'warning' })
    await request.delete(`/api/admin/courses/${row.id}`)
    ElMessage.success('已删除')
    loadCourses()
  } catch { /* ignore */ }
}
</script>

<style scoped>
.ac-page { padding: 0; }
.page-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
.page-title { font-size: 26px; font-weight: 600; color: #1d2129; margin: 0; }
</style>
