<template>
  <el-container class="layout-container">
    <el-aside :width="isCollapsed ? '64px' : '240px'" class="layout-aside">
      <div class="aside-bg">
        <div class="aside-orb orb-tl"></div>
        <div class="aside-orb orb-br"></div>
      </div>
      <div class="logo-area">
        <div class="logo-icon">
          <svg class="logo-svg" viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#5b8def" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
        </div>
        <transition name="fade">
          <span v-if="!isCollapsed" class="logo-text">AI 课程答疑</span>
        </transition>
      </div>
      <div class="role-badge">
        <el-tag :type="roleTagType" size="small" effect="dark" round>{{ roleLabel }}</el-tag>
      </div>
      <el-menu :default-active="activeMenu" :collapse="isCollapsed" :router="true" class="aside-menu">
        <template v-if="role === 'student'">
          <el-menu-item index="/courses"><el-icon><Notebook /></el-icon><span>课程列表</span></el-menu-item>
          <el-menu-item index="/courseware"><el-icon><FolderOpened /></el-icon><span>课件管理</span></el-menu-item>
          <el-menu-item index="/chat"><el-icon><ChatDotRound /></el-icon><span>AI 问答</span></el-menu-item>
          <el-menu-item index="/ask-teacher"><el-icon><Message /></el-icon><span>向老师提问</span></el-menu-item>
          <el-menu-item index="/knowledge-graph"><el-icon><Share /></el-icon><span>知识图谱</span></el-menu-item>
          <el-menu-item index="/statistics"><el-icon><DataAnalysis /></el-icon><span>提问统计</span></el-menu-item>
        </template>
        <template v-if="role === 'teacher'">
          <el-menu-item index="/teacher/dashboard"><el-icon><Odometer /></el-icon><span>教师面板</span></el-menu-item>
          <el-menu-item index="/teacher/courses"><el-icon><Notebook /></el-icon><span>课程管理</span></el-menu-item>
          <el-menu-item index="/teacher/courseware"><el-icon><FolderOpened /></el-icon><span>课件管理</span></el-menu-item>
          <el-menu-item index="/teacher/chat"><el-icon><ChatDotRound /></el-icon><span>AI 问答</span></el-menu-item>
          <el-menu-item index="/teacher/answer-questions"><el-icon><Edit /></el-icon><span>回答问题</span></el-menu-item>
          <el-menu-item index="/teacher/knowledge-graph"><el-icon><Share /></el-icon><span>知识图谱</span></el-menu-item>
          <el-menu-item index="/teacher/statistics"><el-icon><DataAnalysis /></el-icon><span>教学统计</span></el-menu-item>
        </template>
        <template v-if="role === 'admin'">
          <el-menu-item index="/admin/dashboard"><el-icon><Odometer /></el-icon><span>管理面板</span></el-menu-item>
          <el-menu-item index="/admin/users"><el-icon><User /></el-icon><span>用户管理</span></el-menu-item>
          <el-menu-item index="/admin/courses"><el-icon><Notebook /></el-icon><span>课程管理</span></el-menu-item>
        </template>
      </el-menu>
      <div class="sidebar-footer">
        <el-button text class="collapse-btn" @click="isCollapsed = !isCollapsed">
          <el-icon :size="16"><Fold /></el-icon>
          <span v-if="!isCollapsed">收起侧边栏</span>
        </el-button>
      </div>
    </el-aside>
    <el-container>
      <el-header class="layout-header">
        <div class="header-left">
          <el-breadcrumb separator="›" class="header-breadcrumb">
            <el-breadcrumb-item :to="{ path: homePath }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="route.meta?.title">{{ route.meta.title }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-popover placement="bottom" :width="380" trigger="click" popper-class="noti-popover">
            <template #reference>
              <el-badge :value="unreadCount" :hidden="unreadCount === 0" class="noti-badge" :max="99">
                <el-button :icon="Bell" text class="noti-btn" />
              </el-badge>
            </template>
            <div class="noti-panel">
              <div class="noti-header">
                <span class="noti-title">通知</span>
                <el-button text size="small" @click="handleMarkAllRead">全部已读</el-button>
              </div>
              <div class="noti-list" v-if="notifications.length">
                <div v-for="n in notifications" :key="n.id" class="noti-item" :class="{ unread: !n.is_read }" @click="handleMarkRead(n)">
                  <div class="noti-dot" v-if="!n.is_read"></div>
                  <div class="noti-body">
                    <div class="noti-item-title">{{ n.title }}</div>
                    <div class="noti-item-content">{{ n.content }}</div>
                    <div class="noti-item-time">{{ n.created_at }}</div>
                  </div>
                </div>
              </div>
              <el-empty v-else :image-size="32" description="暂无通知" />
            </div>
          </el-popover>
          <el-dropdown trigger="click" @command="handleCommand">
            <span class="user-info">
              <el-avatar :size="32" icon="UserFilled" :style="{ background: avatarColor }" />
              <span class="user-name">{{ userStore.userInfo?.username || '用户' }}</span>
              <el-icon class="dropdown-arrow"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-item command="logout"><el-icon><SwitchButton /></el-icon>退出登录</el-dropdown-item>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="layout-main">
        <div class="main-bg-orb orb-m1"></div>
        <div class="main-bg-orb orb-m2"></div>
        <router-view v-slot="{ Component }">
          <transition name="page-fade" mode="out-in">
            <component :is="Component" :key="route.path" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import {
  Notebook, FolderOpened, ChatDotRound, Message, Fold,
  UserFilled, SwitchButton, Bell, Odometer, User, Share,
  DataAnalysis, Edit, ArrowDown
} from '@element-plus/icons-vue'
import { getUnreadCount, listNotifications, markAllRead, markRead } from '../api/notification'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const isCollapsed = ref(false)
const role = computed(() => userStore.userInfo?.role || 'student')
const roleLabel = computed(() => ({ student: '学生', teacher: '教师', admin: '管理员' }[role.value] || '学生'))
const roleTagType = computed(() => ({ student: '', teacher: 'success', admin: 'danger' }[role.value] || ''))
const avatarColor = computed(() => ({ student: '#5b8def', teacher: '#67c23a', admin: '#f56c6c' }[role.value] || '#5b8def'))
const unreadCount = ref(0)
const notifications = ref([])

onMounted(async () => { await fetchUnreadCount(); setInterval(fetchUnreadCount, 30000) })
async function fetchUnreadCount() {
  try { const res = await getUnreadCount(); unreadCount.value = res.data?.count || 0; if (unreadCount.value > 0) { const listRes = await listNotifications(); notifications.value = listRes.data?.notifications || [] } } catch {}
}
async function handleMarkAllRead() { try { await markAllRead(); unreadCount.value = 0; notifications.value = [] } catch {} }
async function handleMarkRead(n) {
  if (n.is_read) return; try { await markRead(n.id); n.is_read = true; unreadCount.value = Math.max(0, unreadCount.value - 1) } catch {}
  if (n.related_id) { const r = userStore.userInfo?.role || 'student'; if (n.type === 'answer') router.push('/ask-teacher'); else if (n.type === 'question') router.push(r === 'teacher' ? '/teacher/answer-questions' : '/ask-teacher') }
}
const homePath = computed(() => ({ student: '/courses', teacher: '/teacher/dashboard', admin: '/admin/dashboard' }[role.value] || '/courses'))
const activeMenu = computed(() => {
  const path = route.path; const segs = path.split('/').filter(Boolean)
  if (segs.length && /^\d+$/.test(segs[segs.length - 1])) segs.pop()
  if (role.value === 'student' || !role.value) return '/' + segs.slice(0, 2).join('/')
  return '/' + segs.slice(0, 3).join('/')
})
function handleCommand(cmd) { if (cmd === 'logout') { userStore.logout(); router.push('/login') } }
</script>

<style scoped>
.layout-container { height: 100vh; background: var(--bg-primary); }

/* ===== Sidebar ===== */
.layout-aside {
  background: linear-gradient(180deg, #0a1929 0%, #0d2137 50%, #0f1f30 100%);
  transition: width var(--transition-normal);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 20px rgba(0,0,0,0.25);
  z-index: 10;
  position: relative;
}
.aside-bg { position: absolute; inset: 0; pointer-events: none; overflow: hidden; }
.aside-orb {
  position: absolute; border-radius: 50%; filter: blur(60px); opacity: 0.15;
}
.orb-tl { width: 300px; height: 300px; background: radial-gradient(circle, #5b8def, #409eff); top: -15%; left: -20%; animation: orb-drift 12s ease-in-out infinite; }
.orb-br { width: 250px; height: 250px; background: radial-gradient(circle, #5b8def, #1a3a5c); bottom: -10%; right: -15%; animation: orb-drift 15s ease-in-out infinite reverse; }
@keyframes orb-drift { 0%,100% { transform: translate(0,0) scale(1); } 33% { transform: translate(10px,-10px) scale(1.05); } 66% { transform: translate(-5px,8px) scale(0.95); } }

.logo-area {
  height: 64px; display: flex; align-items: center; justify-content: center; gap: 10px;
  border-bottom: 1px solid rgba(255,255,255,0.06); flex-shrink: 0; padding: 0 16px; position: relative; z-index: 1;
}
.logo-icon {
  flex-shrink: 0; display: flex; align-items: center; justify-content: center;
  width: 36px; height: 36px; background: rgba(91,141,239,0.2); border-radius: 10px;
  backdrop-filter: blur(4px); box-shadow: 0 0 20px rgba(91,141,239,0.1);
}
.logo-text { font-size: 18px; font-weight: 700; color: #e8ecf4; white-space: nowrap; letter-spacing: 0.5px; }
.role-badge { text-align: center; padding: 14px 0 10px; flex-shrink: 0; position: relative; z-index: 1; }
.aside-menu {
  border-right: none; flex: 1; position: relative; z-index: 1;
  --el-menu-item-height: 42px;
  --el-menu-bg-color: transparent;
  --el-menu-text-color: rgba(160,174,192,0.7);
  --el-menu-active-color: #5b8def;
  --el-menu-hover-bg-color: rgba(91,141,239,0.08);
}
.aside-menu :deep(.el-menu-item) {
  margin: 2px 10px; border-radius: 10px; font-size: 14px;
  transition: all var(--transition-fast);
}
.aside-menu :deep(.el-menu-item:hover) {
  color: rgba(160,174,192,0.95) !important;
}
.aside-menu .el-menu-item.is-active {
    background: rgba(255,255,255,0.05);
    color: #5b8def !important; font-weight: 600;
    box-shadow: inset 4px 0 0 #5b8def;
  }

.aside-menu :deep(.el-menu-item .el-icon) { font-size: 18px; }
  .aside-menu :deep(.el-menu-item .el-icon) { font-size: 18px; transition: all 0.25s ease; }
  .aside-menu :deep(.el-menu-item:hover .el-icon) { color: #8ab4ff; transform: scale(1.05); }
.sidebar-footer {
  flex-shrink: 0; border-top: 1px solid rgba(255,255,255,0.06); padding: 8px; position: relative; z-index: 1;
}
.collapse-btn {
  width: 100%; color: rgba(160,174,192,0.5); justify-content: center; gap: 6px; font-size: 12px; padding: 8px;
  transition: color var(--transition-fast); border-radius: 8px;
}
.collapse-btn:hover { color: rgba(160,174,192,0.85); background: rgba(255,255,255,0.04); }

/* ===== Header ===== */
.layout-header {
  display: flex; align-items: center; justify-content: space-between;
  background: rgba(244,247,253,0.9); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid rgba(240,240,240,0.8); padding: 0 28px; height: 56px;
  position: sticky; top: 0; z-index: 9;
}
.header-left { display: flex; align-items: center; gap: 16px; }
.header-breadcrumb :deep(.el-breadcrumb__inner) { font-size: 14px; font-weight: 500; color: var(--text-secondary); }
.header-breadcrumb :deep(.el-breadcrumb__inner.is-link) { color: var(--text-tertiary); }
.header-breadcrumb :deep(.el-breadcrumb__inner.is-link:hover) { color: var(--primary); }
.header-right { display: flex; align-items: center; gap: 8px; }
.noti-badge { margin-right: 4px; }
:deep(.el-badge__content) { top: 4px; right: 2px; }
.noti-btn { border: none; font-size: 20px; color: var(--text-secondary); width: 36px; height: 36px; border-radius: 8px; transition: all var(--transition-fast); }
.noti-btn:hover { color: var(--primary); background: var(--primary-light); }
.noti-popover { padding: 0 !important; }
.noti-panel { max-height: 420px; overflow: hidden; display: flex; flex-direction: column; }
.noti-header { display: flex; align-items: center; justify-content: space-between; padding: 16px 20px 12px; border-bottom: 1px solid #f0f0f0; }
.noti-title { font-size: 15px; font-weight: 600; color: var(--text-primary); }
.noti-list { flex: 1; overflow-y: auto; }
.noti-item { display: flex; align-items: flex-start; gap: 10px; padding: 12px 20px; cursor: pointer; border-bottom: 1px solid #f5f5f5; transition: background var(--transition-fast); }
.noti-item:hover { background: #f5f7fa; }
.noti-item.unread { background: #f0f7ff; }
.noti-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--primary); flex-shrink: 0; margin-top: 6px; }
.noti-body { flex: 1; min-width: 0; }
.noti-item-title { font-size: 14px; color: var(--text-primary); font-weight: 500; line-height: 1.4; }
.noti-item-content { font-size: 13px; color: var(--text-secondary); line-height: 1.4; margin-top: 2px; overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
.noti-item-time { font-size: 12px; color: var(--text-muted); margin-top: 4px; }

.user-info { display: flex; align-items: center; gap: 8px; cursor: pointer; padding: 6px 12px 6px 8px; border-radius: 10px; transition: all var(--transition-fast); }
.user-info:hover { background: #f0f4ff; }
.user-name { font-size: 14px; color: var(--text-primary); font-weight: 500; max-width: 100px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.dropdown-arrow { font-size: 12px; color: var(--text-muted); transition: transform var(--transition-fast); }
.user-info:hover .dropdown-arrow { transform: rotate(180deg); }

/* ===== Main Content ===== */
.layout-main {
  background: var(--bg-gradient-rich);
  padding: 24px;
  overflow-y: auto;
  position: relative;
}
.main-bg-orb {
  position: fixed; border-radius: 50%; filter: blur(100px); pointer-events: none; z-index: 0;
}
.orb-m1 { width: 500px; height: 500px; background: radial-gradient(circle, rgba(64,158,255,0.06), transparent); top: -10%; right: -5%; }
.orb-m2 { width: 400px; height: 400px;
.orb-m3 { width: 300px; height: 300px; background: radial-gradient(circle, rgba(82,184,89,0.04), transparent); top: 40%; right: 30%; } background: radial-gradient(circle, rgba(124,58,237,0.05), transparent); bottom: -5%; left: -3%; }

.page-fade-enter-active { transition: opacity 0.25s, transform 0.25s; }
.page-fade-leave-active { transition: opacity 0.15s; }
.page-fade-enter-from { opacity: 0; transform: translateY(10px); }
.page-fade-leave-to { opacity: 0; }
</style>
