<template>
  <div class="ad-page">
    <div class="page-head">
      <div class="page-head-left"><h2 class="page-title">管理面板</h2><p class="page-subtitle">系统运行概况</p></div>
    </div>
    <div class="stats-grid">
      <div class="stat-card" v-for="s in stats" :key="s.label">
        <div class="stat-glow" :style="{ background: s.color }"></div>
        <div class="stat-icon-wrap" :style="{ background: s.bg }"><el-icon :size="22" :color="s.color"><component :is="s.icon" /></el-icon></div>
        <div class="stat-body"><div class="stat-value">{{ s.value }}</div><div class="stat-label">{{ s.label }}</div></div>
      </div>
    </div>
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card shadow="never" class="manage-card" @click="$router.push('/admin/users')">
          <template #header><span><el-icon><User /></el-icon> 用户管理</span></template>
          <p class="manage-desc">管理所有用户账号和角色</p>
          <el-button type="primary" plain size="large">管理用户</el-button>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never" class="manage-card" @click="$router.push('/admin/courses')">
          <template #header><span><el-icon><Notebook /></el-icon> 课程管理</span></template>
          <p class="manage-desc">管理平台上的所有课程</p>
          <el-button type="primary" plain size="large">管理课程</el-button>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { UserFilled, Notebook, FolderOpened, User } from '@element-plus/icons-vue'
import request from '../../api/request'
const stats = ref([{ label: '用户总数', value: 0, icon: 'UserFilled', bg: '#e6f7ff', color: '#1890ff' }, { label: '课程总数', value: 0, icon: 'Notebook', bg: '#f0f9eb', color: '#67c23a' }, { label: '课件总数', value: 0, icon: 'FolderOpened', bg: '#fef0f0', color: '#f56c6c' }])
onMounted(async () => { try { const res = await request.get('/api/admin/stats'); const d = res.data; if (d) { stats.value[0].value = d.users || 0; stats.value[1].value = d.courses || 0; stats.value[2].value = d.courseware || 0 } } catch {} })
</script>
<style scoped>
.ad-page { padding: 0; }
.page-head { margin-bottom: 28px; position: relative; }
.page-head::before { content: ""; position: absolute; top: -4px; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, #4a7cff,#7c5ce7); border-radius: 2px; opacity: 0.4; }
.page-title { font-size: 26px; font-weight: 700; color: var(--text-primary); margin: 0; letter-spacing: -0.5px; }
.page-title::after { content: ""; display: block; width: 36px; height: 3px; background: linear-gradient(90deg, #4a7cff, #7c5ce7); border-radius: 2px; margin-top: 8px; opacity: 0.4; }
.page-subtitle { font-size: 14px; color: var(--text-tertiary); margin-top: 4px; }
.stats-deco { height: 3px; background: linear-gradient(90deg, #4a7cff, #7c5ce7, #52b859, #e8923a); border-radius: 2px; margin-bottom: 24px; opacity: 0.5; }
.stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 28px; }
.stat-card { background: var(--bg-card); border-radius: 14px; padding: 24px; display: flex; align-items: center; gap: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border: 1px solid var(--border-light); transition: all var(--transition-normal); position: relative; overflow: hidden; }
.stat-card:hover { box-shadow: 0 8px 24px rgba(0,0,0,0.08); transform: translateY(-2px); }
.stat-glow { position: absolute; top: 0; left: 0; width: 100%; height: 3px; opacity: 0.6; }
.stat-icon-wrap { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.stat-value { font-size: 28px; font-weight: 700; color: var(--text-primary); line-height: 1.2; }
.stat-label { font-size: 14px; color: var(--text-tertiary); margin-top: 4px; }
.manage-card { border-radius: 14px !important; text-align: center; padding: 16px 0; cursor: pointer; transition: all var(--transition-normal); }
.manage-card:hover { box-shadow: 0 8px 24px rgba(0,0,0,0.08) !important; transform: translateY(-2px); }
.manage-card :deep(.el-card__header) { font-size: 17px; font-weight: 600; }
.manage-desc { font-size: 14px; color: var(--text-tertiary); margin-bottom: 16px; }
</style>



