 <template>
   <div class="chat-page">
     <div class="chat-main" ref="chatRef">
       <div v-if="!messages.length" class="chat-empty">
         <el-icon :size="48" color="#c0c4cc"><ChatDotRound /></el-icon>
         <p>你好！我是 AI 课程助手，请提出课程相关问题</p>
       </div>
       <div v-for="(msg, i) in messages" :key="i" :class="['msg-row', msg.role]">
         <div class="msg-avatar">
           <el-avatar :size="36" :icon="msg.role === 'user' ? UserFilled : Promotion" />
         </div>
         <div class="msg-bubble">
           <div class="msg-text">{{ msg.content }}</div>
           <div v-if="msg.sources?.length" class="msg-sources">
             <span class="source-label">参考来源：</span>
             <el-tag v-for="(s, j) in msg.sources" :key="j" size="small">{{ s }}</el-tag>
           </div>
           <div v-if="msg.role === 'assistant'" class="msg-actions">
           <el-button text size="small" circle @click="rateMessage(i, 'like')">
             <el-icon><svg viewBox="0 0 24 24" width="16" height="16"><path fill="currentColor" d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54z"/></svg></el-icon>
           </el-button>
           <el-button text size="small" circle @click="rateMessage(i, 'dislike')">
             <el-icon><svg viewBox="0 0 24 24" width="16" height="16"><path fill="currentColor" d="M12 2.65l1.45 1.32C18.6 8.64 22 11.72 22 15.5 22 18.58 19.58 21 16.5 21c-1.74 0-3.41-.81-4.5-2.09C10.91 20.19 9.24 21 7.5 21 4.42 21 2 18.58 2 15.5c0-3.78 3.4-6.86 8.55-11.54z"/></svg></el-icon>
           </el-button>
           </div>
         </div>
       </div>
       <div v-if="loading" class="msg-row assistant">
         <div class="msg-avatar"><el-avatar :size="36" :icon="Promotion" /></div>
         <div class="msg-bubble"><span class="typing-dot">.</span><span class="typing-dot">.</span><span class="typing-dot">.</span></div>
       </div>
     </div>
     <div class="chat-input-area">
       <el-input
         v-model="inputText"
         placeholder="输入你的问题..."
         :disabled="loading"
         @keyup.enter="sendMessage"
       >
         <template #append>
           <el-button :disabled="!inputText.trim() || loading" @click="sendMessage">发送</el-button>
         </template>
       </el-input>
     </div>
   </div>
 </template>
 
 <script setup>
 import { ref, nextTick } from 'vue'
 import { useRoute } from 'vue-router'
 import { ChatDotRound, UserFilled, Promotion } from '@element-plus/icons-vue'
 import request from '../api/request'
 
 const route = useRoute()
 const chatRef = ref(null)
 const inputText = ref('')
 const messages = ref([])
 const loading = ref(false)
 
 async function sendMessage() {
   const text = inputText.value.trim()
   if (!text || loading.value) return
   inputText.value = ''
   messages.value.push({ role: 'user', content: text })
   loading.value = true
   scrollDown()
   try {
     const res = await request.post('/api/chat', {
       message: text,
       course_id: route.params.courseId || null
     })
     messages.value.push({
       role: 'assistant',
       content: res.answer || res.response || '暂无回答',
       sources: res.sources || []
     })
   } catch {
     messages.value.push({ role: 'assistant', content: '抱歉，暂时无法回答，请稍后再试。', sources: [] })
   } finally {
     loading.value = false
     scrollDown()
   }
 }
 
 function rateMessage(index, type) {
   const msg = messages.value[index]
   request.post('/api/chat/feedback', { message_id: msg.id, type }).catch(() => {})
 }
 
 function scrollDown() {
   nextTick(() => {
     chatRef.value?.scrollTo({ top: chatRef.value.scrollHeight, behavior: 'smooth' })
   })
 }
 </script>
 
 <style scoped>
 .chat-page { display: flex; flex-direction: column; height: calc(100vh - 100px); }
 .chat-main { flex: 1; overflow-y: auto; padding: 16px; background: #fff; border-radius: 8px; margin-bottom: 16px; }
 .chat-empty { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; color: #909399; gap: 12px; }
 .msg-row { display: flex; gap: 12px; margin-bottom: 20px; }
 .msg-row.user { flex-direction: row-reverse; }
 .msg-avatar { flex-shrink: 0; }
 .msg-bubble { max-width: 70%; padding: 12px 16px; border-radius: 12px; font-size: 14px; line-height: 1.6; }
 .msg-row.user .msg-bubble { background: #409eff; color: #fff; border-bottom-right-radius: 4px; }
 .msg-row.assistant .msg-bubble { background: #f0f2f5; color: #333; border-bottom-left-radius: 4px; }
 .msg-sources { margin-top: 8px; display: flex; flex-wrap: wrap; gap: 4px; align-items: center; }
 .source-label { font-size: 12px; color: #909399; }
 .msg-actions { margin-top: 6px; display: flex; gap: 4px; }
 .chat-input-area { flex-shrink: 0; }
 .typing-dot { animation: blink 1.4s infinite both; font-size: 24px; font-weight: bold; }
 .typing-dot:nth-child(2) { animation-delay: 0.2s; }
 .typing-dot:nth-child(3) { animation-delay: 0.4s; }
 @keyframes blink { 0%, 80%, 100% { opacity: 0; } 40% { opacity: 1; } }
 </style>
