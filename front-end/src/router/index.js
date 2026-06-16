 import { createRouter, createWebHistory } from 'vue-router'
 
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
       {
         path: 'courses',
         name: 'Courses',
         component: () => import('../views/CourseListView.vue'),
         meta: { title: '课程列表', icon: 'Notebook' }
       },
       {
         path: 'courseware',
         name: 'Courseware',
         component: () => import('../views/CoursewareView.vue'),
         meta: { title: '课件管理', icon: 'FolderOpened' }
       },
       {
         path: 'chat/:courseId?',
         name: 'Chat',
         component: () => import('../views/ChatView.vue'),
         meta: { title: 'AI 问答', icon: 'ChatDotRound' }
       },
       {
         path: 'knowledge-graph/:courseId?',
         name: 'KnowledgeGraph',
         component: () => import('../views/KnowledgeGraphView.vue'),
         meta: { title: '知识图谱', icon: 'Share' }
       },
       {
         path: 'statistics',
         name: 'Statistics',
         component: () => import('../views/StatisticsView.vue'),
         meta: { title: '提问统计', icon: 'DataAnalysis' }
       }
     ]
   }
 ]
 
 const router = createRouter({
   history: createWebHistory(),
   routes
 })
 
 export default router
