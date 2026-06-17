 <template>
   <div class="ts-page">
     <div class="page-head">
       <h2 class="page-title">教学统计</h2>
     </div>
     <el-tabs v-model="activeTab">
       <el-tab-pane label="学生提问" name="questions">
         <el-table :data="studentQuestions" v-loading="loading" stripe>
           <el-table-column prop="student_name" label="提问学生" width="120" />
           <el-table-column prop="title" label="问题标题" min-width="180" />
           <el-table-column prop="course_name" label="课程" width="120" />
           <el-table-column prop="content" label="问题内容" min-width="240" show-overflow-tooltip />
           <el-table-column prop="status" label="状态" width="90">
             <template #default="{ row }">
               <el-tag :type="row.status === 'answered' ? 'success' : 'warning'" size="small" round>
                 {{ row.status === 'answered' ? '已回复' : '待回复' }}
               </el-tag>
             </template>
           </el-table-column>
           <el-table-column label="操作" width="160">
             <template #default="{ row }">
               <template v-if="row.status !== 'answered'">
                 <el-popover placement="left" :width="320" trigger="click">
                   <template #reference>
                     <el-button text type="primary" size="small">回复</el-button>
                   </template>
                   <div class="reply-popover">
                     <p class="reply-question">{{ row.content }}</p>
                     <el-input v-model="row.replyText" type="textarea" :rows="3" placeholder="输入回复..." />
                     <el-button type="primary" size="small" style="margin-top:8px" @click="replyQuestion(row)">发送回复</el-button>
                   </div>
                 </el-popover>
               </template>
               <span v-else class="replied-text">已回复</span>
             </template>
           </el-table-column>
         </el-table>
         <el-empty v-if="!loading && !studentQuestions.length" :image-size="60" description="暂无学生提问" />
       </el-tab-pane>
       <el-tab-pane label="分析数据" name="stats">
         <el-empty :image-size="60" description="等待后端数据" />
       </el-tab-pane>
     </el-tabs>
   </div>
 </template>
 
 <script setup>
 import { ref, onMounted } from 'vue'
 import { ElMessage } from 'element-plus'
 import request from '../../api/request'
 
 const activeTab = ref('questions')
 const loading = ref(false)
 const studentQuestions = ref([])
 
 onMounted(loadQuestions)
 
 async function loadQuestions() {
   loading.value = true
   try {
     const res = await request.get('/api/ask-teacher')
     studentQuestions.value = (res.questions || []).map(q => ({ ...q, replyText: '' }))
   } catch { studentQuestions.value = [] }
   loading.value = false
 }
 
 async function replyQuestion(row) {
   if (!row.replyText) { ElMessage.warning('请输入回复内容'); return }
   try {
     await request.post('/api/ask-teacher/' + row.id + '/reply', { answer: row.replyText })
     ElMessage.success('已回复')
     loadQuestions()
   } catch { /* ignore */ }
 }
 </script>
 
 <style scoped>
 .ts-page { padding: 0; }
 .page-head { margin-bottom: 20px; }
 .page-title { font-size: 26px; font-weight: 600; color: #1d2129; margin: 0; }
 .reply-popover { padding: 4px; }
 .reply-question { font-size: 17px; color: #86909c; background: #f7f8fa; padding: 8px 12px; border-radius: 6px; margin: 0 0 12px; }
 .replied-text { font-size: 17px; color: #67c23a; }
 </style>
