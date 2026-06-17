 <template>
  <div class="chat-page">
    <div class="chat-header">
      <div class="chat-header-info">
        <el-icon :size="20" color="#409eff"><ChatDotRound /></el-icon>
        <span>AI 问答</span>
      </div>
      <div class="chat-header-actions">
        <el-select v-model="selectedCourseId" placeholder="全部课程" clearable size="small" style="width:180px" @change="clearChat">
          <el-option v-for="c in courseList" :key="c.id" :label="c.course_name" :value="c.id" />
        </el-select>
        <el-button text :icon="Delete" @click="clearChat">清空对话</el-button>
      </div>
    </div>
    <div class="chat-body" ref="chatRef">
      <div v-if="!messages.length" class="chat-empty">
        <div class="empty-icon">
          <el-icon :size="56" color="#d0d5dd"><ChatDotRound /></el-icon>
        </div>
        <p class="empty-title">你好！我是 AI 课程助手</p>
        <p class="empty-desc">请提出课程相关问题，我会基于课件内容为你解答</p>
        <div class="empty-hints">
          <el-tag
            v-for="hint in hints"
            :key="hint"
            closable
            :disable-transitions="false"
            @click="sendHint(hint)"
            @close.stop
          >
            {{ hint }}
          </el-tag>
        </div>
      </div>
      <div v-for="(msg, i) in messages" :key="i" :class="['msg-row', msg.role]">
        <div class="msg-avatar">
          <el-avatar
            :size="36"
            :icon="msg.role === 'user' ? UserFilled : Promotion"
            :style="msg.role === 'user' ? { background: '#409eff' } : { background: '#e6f4ff' }"
          />
        </div>
        <div class="msg-content">
          <div class="msg-role">{{ msg.role === 'user' ? '你' : 'AI 助手' }}</div>
          <div class="msg-bubble">
            <div class="msg-text">{{ msg.content }}</div>
            <div v-if="msg.sources?.length" class="msg-sources">
              <span class="source-label">参考来源：</span>
              <el-tag v-for="(s, j) in msg.sources" :key="j" size="small" round>{{ s }}</el-tag>
            </div>
          </div>
          <div v-if="msg.role === 'assistant'" class="msg-actions">
            <el-tooltip content="有帮助" placement="top">
              <el-button text size="small" circle @click="rateMessage(i, 'like')">
                <el-icon><svg viewBox="0 0 24 24" width="14" height="14"><path fill="currentColor" d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54z"/></svg></el-icon>
              </el-button>
            </el-tooltip>
            <el-tooltip content="没有帮助" placement="top">
              <el-button text size="small" circle @click="rateMessage(i, 'dislike')">
                <el-icon><svg viewBox="0 0 24 24" width="14" height="14"><path fill="currentColor" d="M12 2.65l1.45 1.32C18.6 8.64 22 11.72 22 15.5 22 18.58 19.58 21 16.5 21c-1.74 0-3.41-.81-4.5-2.09C10.91 20.19 9.24 21 7.5 21 4.42 21 2 18.58 2 15.5c0-3.78 3.4-6.86 8.55-11.54z"/></svg></el-icon>
              </el-button>
            </el-tooltip>
          </div>
        </div>
      </div>
      <div v-if="loading" class="msg-row assistant">
        <div class="msg-avatar"><el-avatar :size="36" icon="Promotion" style="background:#e6f4ff" /></div>
        <div class="msg-content">
          <div class="msg-role">AI 助手</div>
          <div class="msg-bubble">
            <span class="dot-pulse"></span>
          </div>
        </div>
      </div>
    </div>
    <div class="chat-input-bar">
      <el-input
        v-model="inputText"
        placeholder="输入你的问题..."
        :disabled="loading"
        size="large"
        @keyup.enter="sendMessage"
      >
        <template #append>
          <el-button
            type="primary"
            :disabled="!inputText.trim() || loading"
            @click="sendMessage"
            :icon="Position"
          />
        </template>
      </el-input>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { ChatDotRound, UserFilled, Promotion, Delete, Position } from '@element-plus/icons-vue'
import request from '../api/request'
import { listCourses } from '../api/course'

const route = useRoute()
const chatRef = ref(null)
const inputText = ref('')
const messages = ref([])
const loading = ref(false)
const courseList = ref([])
const selectedCourseId = ref(null)

const hints = ['这门课主要讲什么？', '帮我梳理第二章的知识点', '这道题应该怎么理解？']

onMounted(async () => {
  // 从 URL 参数获取课程 ID
  const urlCourseId = route.params.courseId || route.query.course_id
  if (urlCourseId) selectedCourseId.value = Number(urlCourseId)

  // 加载用户课程列表
  try {
    const res = await listCourses()
    courseList.value = res.data?.courses || []
  } catch { courseList.value = [] }
})

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
      course_id: selectedCourseId.value || null
    })
    messages.value.push({
      role: 'assistant',
      content: res.data?.answer || res.answer || '暂无回答',
      sources: res.data?.sources || []
    })
  } catch {
    messages.value.push({ role: 'assistant', content: '抱歉，暂时无法回答，请稍后再试。', sources: [] })
  } finally {
    loading.value = false
    scrollDown()
  }
}

function sendHint(hint) {
  inputText.value = hint
  sendMessage()
}

function clearChat() {
  messages.value = []
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
.chat-page {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 112px);
  background: linear-gradient(180deg, #f8faff 0%, #f0f4ff 30%, #eef2ff 70%, #f5f0ff 100%);
  border-radius: 8px;
  overflow: hidden;
}
.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  background: rgba(255,255,255,0.85);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid #e4e7ed;
  flex-shrink: 0;
}
.chat-header-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 20px;
  font-weight: 600;
  color: #1d2129;
}
.chat-header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}
.chat-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  scroll-behavior: smooth;
}
.chat-body::-webkit-scrollbar { width: 6px; }
.chat-body::-webkit-scrollbar-thumb { background: #d0d5dd; border-radius: 3px; }
.chat-body::-webkit-scrollbar-track { background: transparent; }
.chat-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 40px;
}
.empty-icon { margin-bottom: 16px; }
.empty-title { font-size: 24px; font-weight: 600; color: #1d2129; margin: 0 0 6px; }
.empty-desc { font-size: 18px; color: #86909c; margin: 0 0 24px; }
.empty-hints { display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; }
.empty-hints .el-tag { cursor: pointer; }
.msg-row {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  animation: msg-in 0.25s ease-out;
}
@keyframes msg-in {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
.msg-row.user { flex-direction: row-reverse; }
.msg-avatar { flex-shrink: 0; }
.msg-content { max-width: 70%; }
.msg-row.user .msg-content { display: flex; flex-direction: column; align-items: flex-end; }
.msg-role { font-size: 16px; color: #86909c; margin-bottom: 6px; }
.msg-bubble {
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 18px;
  line-height: 1.7;
  word-break: break-word;
}
.msg-row.user .msg-bubble {
  background: linear-gradient(135deg, #409eff, #337ecc);
  color: #fff;
  border-bottom-right-radius: 2px;
}
.msg-row.assistant .msg-bubble {
  background: #f7f8fa;
  color: #1d2129;
  border-bottom-left-radius: 2px;
}
.msg-text { white-space: pre-wrap; }
.msg-sources { margin-top: 8px; display: flex; flex-wrap: wrap; gap: 4px; align-items: center; }
.source-label { font-size: 16px; color: #909399; }
.msg-actions { margin-top: 6px; display: flex; gap: 4px; padding-left: 4px; }
.chat-input-bar {
  flex-shrink: 0;
  padding: 16px 20px;
  border-top: 1px solid #e4e7ed;
}
.dot-pulse {
  display: flex;
  gap: 4px;
}
.dot-pulse::before,
.dot-pulse::after,
.dot-pulse {
  content: '';
  width: 8px;
  height: 8px;
  background: #909399;
  border-radius: 50%;
  animation: pulse 1.4s infinite both;
}
.dot-pulse::before {
  animation-delay: 0.2s;
}
.dot-pulse::after {
  animation-delay: 0.4s;
}
@keyframes pulse {
  0%, 80%, 100% { opacity: 0.3; }
  40% { opacity: 1; }
}
</style>
