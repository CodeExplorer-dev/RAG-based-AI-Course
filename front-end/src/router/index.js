import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/',
    component: () => import('../layouts/MainLayout.vue'),
    redirect: '/courses',
    children: [
      // 学生/通用 — 课程列表
      { path: 'courses', name: 'Courses', component: () => import('../views/CourseListView.vue'), meta: { title: '课程列表', icon: 'Notebook' } },
      // 课件管理（支持 ?course_id= 参数）
      { path: 'courseware', name: 'Courseware', component: () => import('../views/CoursewareView.vue'), meta: { title: '课件管理', icon: 'FolderOpened' } },
      { path: 'chat/:courseId?', name: 'Chat', component: () => import('../views/ChatView.vue'), meta: { title: 'AI 问答', icon: 'ChatDotRound' } },
      { path: 'ask-teacher', name: 'AskTeacher', component: () => import('../views/AskTeacherView.vue'), meta: { title: '向老师提问', icon: 'Message' } },
      // 以下功能开发中
      { path: 'knowledge-graph/:courseId?', name: 'KnowledgeGraph', component: () => import('../views/KnowledgeGraphView.vue'), meta: { title: '知识图谱', icon: 'Share' } },
      { path: 'statistics', name: 'Statistics', component: () => import('../views/StatisticsView.vue'), meta: { title: '提问统计', icon: 'DataAnalysis' } },
    ]
  },
  {
    path: '/teacher',
    component: () => import('../layouts/MainLayout.vue'),
    redirect: '/teacher/dashboard',
    children: [
      { path: 'dashboard', name: 'TeacherDashboard', component: () => import('../views/teacher/DashboardView.vue'), meta: { title: '教师面板', icon: 'Odometer', roles: ['teacher'] } },
      { path: 'courses', name: 'TeacherCourses', component: () => import('../views/teacher/CoursesView.vue'), meta: { title: '课程管理', icon: 'Notebook', roles: ['teacher'] } },
      { path: 'courseware', name: 'TeacherCourseware', component: () => import('../views/CoursewareView.vue'), meta: { title: '课件管理', icon: 'FolderOpened', roles: ['teacher'] } },
      { path: 'chat/:courseId?', name: 'TeacherChat', component: () => import('../views/ChatView.vue'), meta: { title: 'AI 问答', icon: 'ChatDotRound', roles: ['teacher'] } },
      // 以下功能开发中
      { path: 'knowledge-graph/:courseId?', name: 'TeacherKG', component: () => import('../views/KnowledgeGraphView.vue'), meta: { title: '知识图谱', icon: 'Share', roles: ['teacher'] } },
      { path: 'statistics', name: 'TeacherStats', component: () => import('../views/teacher/StatsView.vue'), meta: { title: '教学统计', icon: 'DataAnalysis', roles: ['teacher'] } },
    ]
  },
  {
    path: '/admin',
    component: () => import('../layouts/MainLayout.vue'),
    redirect: '/admin/dashboard',
    children: [
      { path: 'dashboard', name: 'AdminDashboard', component: () => import('../views/admin/DashboardView.vue'), meta: { title: '管理面板', icon: 'Odometer', roles: ['admin'] } },
      { path: 'users', name: 'UserManagement', component: () => import('../views/admin/UsersView.vue'), meta: { title: '用户管理', icon: 'User', roles: ['admin'] } },
      { path: 'courses', name: 'AdminCourses', component: () => import('../views/admin/CoursesView.vue'), meta: { title: '课程管理', icon: 'Notebook', roles: ['admin'] } },
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  if (to.name !== 'Login' && !userStore.token) {
    return next('/login')
  }
  if (to.meta?.roles && userStore.userInfo?.role) {
    if (!to.meta.roles.includes(userStore.userInfo.role)) {
      const role = userStore.userInfo.role
      const home = { student: '/courses', teacher: '/teacher/dashboard', admin: '/admin/dashboard' }
      return next(home[role] || '/login')
    }
  }
  next()
})

export default router
