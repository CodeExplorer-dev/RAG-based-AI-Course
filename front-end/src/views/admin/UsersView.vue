<template>
  <div class="au-page">
    <div class="page-head"><h2 class="page-title">用户管理</h2><el-tag type="info" size="large" effect="plain" round>共 {{ users.length }} 人</el-tag></div>
    <div class="table-wrap">
      <el-table :data="users" v-loading="loading" stripe size="large">
        <el-table-column prop="id" label="ID" width="60" align="center" />
        <el-table-column prop="username" label="用户名" min-width="150">
          <template #default="{ row }"><div class="user-cell"><el-avatar :size="28" icon="UserFilled" :style="{ background: row.role === 'admin' ? '#f56c6c' : row.role === 'teacher' ? '#67c23a' : '#5b8def' }" /><span>{{ row.username }}</span></div></template>
        </el-table-column>
        <el-table-column prop="email" label="邮箱" min-width="180"><template #default="{ row }">{{ row.email || '-' }}</template></el-table-column>
        <el-table-column prop="role" label="角色" width="120" align="center">
          <template #default="{ row }"><el-tag :type="row.role === 'admin' ? 'danger' : row.role === 'teacher' ? 'success' : 'info'" size="small" round>{{ { student: '学生', teacher: '教师', admin: '管理员' }[row.role] || row.role }}</el-tag></template>
        </el-table-column>
        <el-table-column label="注册时间" width="170" align="center"><template #default="{ row }">{{ formatTime(row.created_at) }}</template></el-table-column>
        <el-table-column label="操作" width="200" align="center">
          <template #default="{ row }">
            <template v-if="row.role !== 'admin'"><el-select :model-value="row.role" size="small" @change="(val) => changeRole(row, val)" style="width: 90px"><el-option label="学生" value="student" /><el-option label="教师" value="teacher" /></el-select><el-button text type="danger" size="small" style="margin-left: 8px" @click="deleteUserFn(row)">删除</el-button></template>
            <el-tag v-else type="danger" size="small">不可操作</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '../../api/request'
import { formatTime } from '../../utils/formatTime'
const loading = ref(false); const users = ref([]); onMounted(loadUsers)
async function loadUsers() { loading.value = true; try { const res = await request.get('/api/admin/users'); users.value = res.data?.users || [] } catch { users.value = [] }; loading.value = false }
async function changeRole(row, newRole) { try { await request.put(`/api/admin/users/${row.id}/role`, { role: newRole }); ElMessage.success('已更新角色'); loadUsers() } catch {} }
async function deleteUserFn(row) { try { await ElMessageBox.confirm(`确定删除用户「${row.username}」吗？`, '提示', { type: 'warning' }); await request.delete(`/api/admin/users/${row.id}`); ElMessage.success('已删除'); loadUsers() } catch {} }
</script>
<style scoped>
.au-page { padding: 0; }
.page-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px;  position: relative; }
.page-title { font-size: 26px; font-weight: 700; color: var(--text-primary); margin: 0; letter-spacing: -0.5px; }
.page-title::after { content: ""; display: block; width: 36px; height: 3px; background: linear-gradient(90deg, #4a7cff, #7c5ce7); border-radius: 2px; margin-top: 8px; opacity: 0.4; }
.table-wrap { background: var(--bg-card); border-radius: var(--radius-lg); box-shadow: var(--shadow-sm); border: 1px solid var(--border-light); overflow: hidden; }
.user-cell { display: flex; align-items: center; gap: 8px; }
</style>


