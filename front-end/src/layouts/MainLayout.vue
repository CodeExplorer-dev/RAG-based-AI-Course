 <template>
   <el-container class="layout-container">
     <el-aside :width="isCollapsed ? '64px' : '220px'" class="layout-aside">
       <div class="logo-area">
         <span v-if="!isCollapsed" class="logo-text">AI 课程答疑</span>
         <span v-else class="logo-mini">AI</span>
       </div>
       <el-menu
         :default-active="activeMenu"
         :collapse="isCollapsed"
         :router="true"
         class="aside-menu"
       >
         <el-menu-item index="/courses">
           <el-icon><Notebook /></el-icon>
           <span>课程列表</span>
         </el-menu-item>
         <el-menu-item index="/courseware">
           <el-icon><FolderOpened /></el-icon>
           <span>课件管理</span>
         </el-menu-item>
         <el-menu-item index="/chat">
           <el-icon><ChatDotRound /></el-icon>
           <span>AI 问答</span>
         </el-menu-item>
         <el-menu-item index="/knowledge-graph">
           <el-icon><Share /></el-icon>
           <span>知识图谱</span>
         </el-menu-item>
         <el-menu-item index="/learning-path">
           <el-icon><TrendCharts /></el-icon>
           <span>学习路径</span>
         </el-menu-item>
         <el-menu-item index="/statistics">
           <el-icon><DataAnalysis /></el-icon>
           <span>提问统计</span>
         </el-menu-item>
       </el-menu>
     </el-aside>
     <el-container>
       <el-header class="layout-header">
         <div class="header-left">
           <el-button :icon="Fold" text @click="isCollapsed = !isCollapsed" />
         </div>
         <div class="header-right">
           <el-dropdown trigger="click">
             <span class="user-info">
               <el-avatar :size="28" :icon="UserFilled" />
               <span class="user-name">{{ userStore.userInfo?.username || '用户' }}</span>
             </span>
             <template #dropdown>
               <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
             </template>
           </el-dropdown>
         </div>
       </el-header>
       <el-main class="layout-main">
         <router-view />
       </el-main>
     </el-container>
   </el-container>
 </template>
 
 <script setup>
 import { ref, computed } from 'vue'
 import { useRoute, useRouter } from 'vue-router'
 import { useUserStore } from '../stores/user'
 import {
   Notebook, FolderOpened, ChatDotRound, Share,
   TrendCharts, DataAnalysis, Fold, UserFilled
 } from '@element-plus/icons-vue'
 
 const route = useRoute()
 const router = useRouter()
 const userStore = useUserStore()
 const isCollapsed = ref(false)
 
 const activeMenu = computed(() => {
   const path = route.path
   return '/' + path.split('/').filter(Boolean)[0]
 })
 
 function handleLogout() {
   userStore.logout()
   router.push('/login')
 }
 </script>
 
 <style scoped>
 .layout-container { height: 100vh; }
 .layout-aside { background-color: #fff; border-right: 1px solid #e4e7ed; transition: width 0.3s; }
 .logo-area { height: 60px; display: flex; align-items: center; justify-content: center; border-bottom: 1px solid #e4e7ed; }
 .logo-text { font-size: 18px; font-weight: 600; color: #409eff; white-space: nowrap; }
 .logo-mini { font-size: 18px; font-weight: 600; color: #409eff; }
 .aside-menu { border-right: none; }
 .layout-header { display: flex; align-items: center; justify-content: space-between; background: #fff; border-bottom: 1px solid #e4e7ed; padding: 0 16px; }
 .header-left { display: flex; align-items: center; }
 .header-right { display: flex; align-items: center; }
 .user-info { display: flex; align-items: center; gap: 8px; cursor: pointer; }
 .user-name { font-size: 14px; color: #333; }
 .layout-main { background-color: #f5f7fa; padding: 20px; }
 </style>
