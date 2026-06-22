<template>
  <el-container class="layout-container">
    <el-aside :width="isCollapsed ? '64px' : '230px'" class="layout-aside">
      <div class="logo-area">
        <div class="logo-icon">
          <el-icon :size="22" color="#5b8def"><ChatDotRound /></el-icon>
        </div>
        <transition name="fade">
          <span v-if="!isCollapsed" class="logo-text">AI 课程答疑</span>
        </transition>
      </div>
      <div class="role-badge">
        <el-tag :type="roleTagType" size="small" effect="dark" round>
          {{ roleLabel }}
        </el-tag>
      </div>
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapsed"
        :router="true"
        class="aside-menu"
      >
        <!-- 学生菜单 -->
        <template v-if="role === 'student'">
          <el-menu-item index="/courses"><el-icon><Notebook /></el-icon><span>课程列表</span></el-menu-item>
          <el-menu-item index="/courseware"><el-icon><FolderOpened /></el-icon><span>课件管理</span></el-menu-item>
          <el-menu-item index="/chat"><el-icon><ChatDotRound /></el-icon><span>AI 问答</span></el-menu-item>
          <el-menu-item index="/ask-teacher"><el-icon><Message /></el-icon><span>向老师提问</span></el-menu-item>
          <el-menu-item index="/knowledge-graph"><el-icon><Share /></el-icon><span>知识图谱</span></el-menu-item>
          <el-menu-item index="/statistics"><el-icon><DataAnalysis /></el-icon><span>提问统计</span></el-menu-item>
        </template>
        <!-- 教师菜单 -->
        <template v-if="role === 'teacher'">
          <el-menu-item index="/teacher/dashboard"><el-icon><Odometer /></el-icon><span>教师面板</span></el-menu-item>
          <el-menu-item index="/teacher/courses"><el-icon><Notebook /></el-icon><span>课程管理</span></el-menu-item>
          <el-menu-item index="/teacher/courseware"><el-icon><FolderOpened /></el-icon><span>课件管理</span></el-menu-item>
          <el-menu-item index="/teacher/chat"><el-icon><ChatDotRound /></el-icon><span>AI 问答</span></el-menu-item>
          <el-menu-item index="/teacher/answer-questions"><el-icon><Edit /></el-icon><span>回答问题</span></el-menu-item>
          <el-menu-item index="/teacher/knowledge-graph"><el-icon><Share /></el-icon><span>知识图谱</span></el-menu-item>
          <el-menu-item index="/teacher/statistics"><el-icon><DataAnalysis /></el-icon><span>教学统计</span></el-menu-item>
        </template>
        <!-- 管理员菜单 -->
        <template v-if="role === 'admin'">
          <el-menu-item index="/admin/dashboard"><el-icon><Odometer /></el-icon><span>管理面板</span></el-menu-item>
          <el-menu-item index="/admin/users"><el-icon><User /></el-icon><span>用户管理</span></el-menu-item>
          <el-menu-item index="/admin/courses"><el-icon><Notebook /></el-icon><span>课程管理</span></el-menu-item>
        </template>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="layout-header">
        <div class="header-left">
          <el-button :icon="Fold" text @click="isCollapsed = !isCollapsed" />
          <el-breadcrumb separator="›" class="header-breadcrumb">
            <el-breadcrumb-item :to="{ path: homePath }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="route.meta?.title">{{ route.meta.title }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-popover placement="bottom" :width="350" trigger="click" popper-class="noti-popover">
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
              <el-avatar :size="28" icon="UserFilled" :style="{ background: avatarColor }" />
              <span class="user-name">{{ userStore.userInfo?.username || '用户' }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-item command="profile"><el-icon><User /></el-icon>个人中心</el-dropdown-item>
              <el-dropdown-item divided command="logout"><el-icon><SwitchButton /></el-icon>退出登录</el-dropdown-item>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="layout-main">
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
import { Notebook, FolderOpened, ChatDotRound, Message, Fold, UserFilled, SwitchButton, Bell, Odometer, User, Share, TrendCharts, DataAnalysis, Edit } from '@element-plus/icons-vue'
import { clearKnowledgePointsCache } from '../views/teacher/AnswerQuestionsView.vue'
import { getUnreadCount, listNotifications, markAllRead, markRead } from '../api/notification'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const isCollapsed = ref(false)

const role = computed(() => userStore.userInfo?.role || 'student')
const roleLabel = computed(() => ({ student: '学生', teacher: '教师', admin: '管理员' }[role.value] || '学生'))
const roleTagType = computed(() => ({ student: 'info', teacher: 'success', admin: 'danger' }[role.value] || 'info'))
const avatarColor = computed(() => ({ student: '#5b8def', teacher: '#67c23a', admin: '#f56c6c' }[role.value] || '#5b8def'))
const unreadCount = ref(0)
const notifications = ref([])

onMounted(async () => {
  await fetchUnreadCount()
  setInterval(fetchUnreadCount, 30000)
})

async function fetchUnreadCount() {
  try {
    const res = await getUnreadCount()
    unreadCount.value = res.data?.count || 0
    if (unreadCount.value > 0) {
      const listRes = await listNotifications()
      notifications.value = listRes.data?.notifications || []
    }
  } catch {}
}

async function handleMarkAllRead() {
  try {
    await markAllRead()
    unreadCount.value = 0
    notifications.value = []
  } catch {}
}

async function handleMarkRead(n) {
  if (n.is_read) return
  try {
    await markRead(n.id)
    n.is_read = true
    unreadCount.value = Math.max(0, unreadCount.value - 1)
  } catch {}
  if (n.related_id) {
    const role = userStore.userInfo?.role || "student"
    if (n.type === "answer") {
      router.push("/ask-teacher")
    } else if (n.type === "question") {
      router.push(role === "teacher" ? "/teacher/answer-questions" : "/ask-teacher")
    }
  }
  if (n.related_id) {
    const r = userStore.userInfo?.role || "student"
    if (n.type === "answer") {
      router.push("/ask-teacher")
    } else if (n.type === "question") {
      router.push(r === "teacher" ? "/teacher/answer-questions" : "/ask-teacher")
    }
  }
}

const homePath = computed(() => ({ student: '/courses', teacher: '/teacher/dashboard', admin: '/admin/dashboard' }[role.value] || '/courses'))

const activeMenu = computed(() => {
  const path = route.path
  const segs = path.split('/').filter(Boolean)
  // 去掉末尾的数字参数（如 courseId）
  if (segs.length && /^\d+$/.test(segs[segs.length - 1])) segs.pop()
  // 学生/通用路由
  if (role.value === 'student' || !role.value) return '/' + segs.slice(0, 2).join('/')
  // 教师/管理员路由
  return '/' + segs.slice(0, 3).join('/')
})

function handleCommand(cmd) {
  if (cmd === 'logout') {
    clearKnowledgePointsCache()
    userStore.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.layout-container { height: 100vh; }
.noti-badge { margin-right: 12px; }
.noti-btn { border: none; font-size: 18px; color: #606266; }
.noti-btn:hover { color: #409eff; background: #f0f5ff; }
.noti-panel { max-height: 400px; overflow: hidden; display: flex; flex-direction: column; }
.noti-header { display: flex; align-items: center; justify-content: space-between; padding: 0 0 10px; border-bottom: 1px solid #f0f0f0; }
.noti-title { font-size: 15px; font-weight: 600; color: #1d2129; }
.noti-list { flex: 1; overflow-y: auto; margin: 0 -12px; padding: 0; }
.noti-item { display: flex; align-items: flex-start; gap: 8px; padding: 10px 12px; cursor: pointer; border-bottom: 1px solid #f5f5f5; transition: background 0.15s; }
.noti-item:hover { background: #f5f7fa; }
.noti-item.unread { background: #f0f7ff; }
.noti-dot { width: 8px; height: 8px; border-radius: 50%; background: #409eff; flex-shrink: 0; margin-top: 6px; }
.noti-body { flex: 1; min-width: 0; }
.noti-item-title { font-size: 14px; color: #1d2129; line-height: 1.4; }
.noti-item-time { font-size: 12px; color: #a8abb2; margin-top: 2px; }
.noti-item-content { font-size: 13px; color: #606266; line-height: 1.4; margin-top: 2px; overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }

.layout-aside {
  background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
.logo-area {
  height: 62px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
  flex-shrink: 0;
}
.logo-icon { flex-shrink: 0; display: flex; align-items: center; }
.logo-text { font-size: 20px; font-weight: 700; color: #e8ecf4; white-space: nowrap; letter-spacing: 1px; }
.role-badge { text-align: center; padding: 12px 0 8px; flex-shrink: 0; }
.aside-menu {
  border-right: none;
  flex: 1;
  font-size: 18px;
  --el-menu-item-height: 46px;
  --el-menu-bg-color: transparent;
  --el-menu-text-color: #a0aec0;
  --el-menu-active-color: #5b8def;
  --el-menu-hover-bg-color: rgba(91, 141, 239, 0.1);
}
.aside-menu :deep(.el-menu-item) {
  font-size: 18px;
}
.aside-menu .el-menu-item.is-active {
  background: linear-gradient(90deg, rgba(91,141,239,0.15) 0%, transparent 100%);
  border-right: 3px solid #5b8def;
}
.layout-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(135deg, #fff 0%, #f8faff 100%);
  border-bottom: 1px solid #eef1f6;
  padding: 0 24px;
  height: 56px;
}
.header-left { display: flex; align-items: center; gap: 16px; }
.header-breadcrumb { font-size: 18px; }
.header-right { display: flex; align-items: center; gap: 12px; }
.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 10px;
  border-radius: 8px;
  transition: background 0.2s;
}
.user-info:hover { background: #f0f4ff; }
.user-name { font-size: 18px; color: #1d2129; font-weight: 500; }
.layout-main {
  background: linear-gradient(135deg, #f5f7fa 0%, #f0f4ff 50%, #f5f0ff 100%);
  padding: 24px;
  overflow-y: auto;
}
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.page-fade-enter-active { transition: opacity 0.2s, transform 0.2s; }
.page-fade-leave-active { transition: opacity 0.15s; }
.page-fade-enter-from { opacity: 0; transform: translateY(8px); }
.page-fade-leave-to { opacity: 0; }
</style>



