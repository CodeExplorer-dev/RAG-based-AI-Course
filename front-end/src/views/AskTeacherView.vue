 <template>
   <div class="ask-page">
     <div class="page-head">
       <h2 class="page-title">向老师提问</h2>
     </div>
     <el-row :gutter="24">
       <el-col :span="14">
         <el-card shadow="never" class="ask-card">
           <template #header><span>提交问题</span></template>
           <el-form :model="form" label-width="0">
             <el-form-item>
               <el-input
                 v-model="form.title"
                 placeholder="问题标题"
                 size="large"
                 clearable
               />
             </el-form-item>
             <el-form-item>
               <el-select
                 v-model="form.course_id"
                 placeholder="选择相关课程"
                 size="large"
                 clearable
                 style="width:100%"
               >
                 <el-option v-for="c in courses" :key="c.id" :label="c.course_name" :value="c.id" />
               </el-select>
             </el-form-item>
             <el-form-item>
               <el-input
                 v-model="form.content"
                 type="textarea"
                 :rows="6"
                 placeholder="详细描述你的问题..."
               />
             </el-form-item>
             <el-form-item>
               <el-button type="primary" size="large" :loading="submitting" @click="submitQuestion">
                 提交问题
               </el-button>
             </el-form-item>
           </el-form>
         </el-card>
       </el-col>
       <el-col :span="10">
         <el-card shadow="never" class="history-card">
           <template #header><span>我的提问历史</span></template>
           <div v-if="myQuestions.length" class="history-list">
             <div v-for="q in myQuestions" :key="q.id" class="history-item">
               <div class="history-title">{{ q.title }}</div>
               <div class="history-meta">
                 <el-tag size="small" :type="q.status === 'answered' ? 'success' : 'warning'" round>
                   {{ q.status === 'answered' ? '已回复' : '待回复' }}
                 </el-tag>
                 <span class="history-time">{{ formatTime(q.created_at) }}</span>
               </div>
               <div v-if="q.answer" class="history-answer">
                 <span class="answer-label">教师回复：</span>
                 {{ q.answer }}
               </div>
             </div>
           </div>
           <el-empty v-else :image-size="60" description="还没有提过问" />
         </el-card>
       </el-col>
     </el-row>
   </div>
 </template>
 
 <script setup>
 import { ref, onMounted } from 'vue'
 import { ElMessage } from 'element-plus'
 import request from '../api/request'
import { formatTime } from '../utils/formatTime'
 
 const courses = ref([])
 const myQuestions = ref([])
 const submitting = ref(false)
 const form = ref({ title: '', course_id: '', content: '' })
 
 onMounted(async () => {
   try {
     const [cRes, qRes] = await Promise.all([
       request.get('/api/courses'),
       request.get('/api/ask-teacher/mine')
     ])
     courses.value = cRes.data?.courses || []
     myQuestions.value = qRes.data?.questions || []
   } catch { /* ignore */ }
 })
 
 async function submitQuestion() {
   if (!form.value.title || !form.value.content) {
     ElMessage.warning('请填写问题标题和内容')
     return
   }
   submitting.value = true
   try {
     await request.post('/api/ask-teacher', form.value)
     ElMessage.success('问题已提交，等待老师回复')
     form.value = { title: '', course_id: '', content: '' }
     const qRes = await request.get('/api/ask-teacher/mine')
     myQuestions.value = qRes.data?.questions || []
   } finally { submitting.value = false }
 }
 </script>
 
 <style scoped>
 .ask-page { padding: 0; }
 .page-head { margin-bottom: 20px; }
 .page-title { font-size: 26px; font-weight: 600; color: #1d2129; margin: 0; }
 .ask-card, .history-card { border-radius: 8px; }
 .history-list { max-height: 500px; overflow-y: auto; }
 .history-item { padding: 14px 0; border-bottom: 1px solid #f0f0f5; }
 .history-item:last-child { border-bottom: none; }
 .history-title { font-size: 18px; font-weight: 500; color: #1d2129; margin-bottom: 6px; }
 .history-meta { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
 .history-time { font-size: 16px; color: #86909c; }
 .history-answer { font-size: 17px; color: #606266; background: #f7f8fa; padding: 8px 12px; border-radius: 6px; margin-top: 6px; }
 .answer-label { color: #67c23a; font-weight: 500; }
 </style>