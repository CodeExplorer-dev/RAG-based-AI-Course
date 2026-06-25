<template>
  <div class="chat-layout" :class="{ 'sidebar-collapsed': !sidebarOpen }">
    <button class="sidebar-toggle" @click="sidebarOpen = !sidebarOpen"
      :title="sidebarOpen ? '收起侧边栏' : '展开侧边栏'">
      <el-icon :size="16"><component :is="sidebarOpen ? 'Fold' : 'Expand'" /></el-icon>
    </button>

    <div class="chat-sidebar">
      <div class="sidebar-header">
        <div class="sidebar-header-left">
          <el-icon :size="18" color="#409eff"><ChatSquare /></el-icon>
          <span class="sidebar-title">历史对话</span>
        </div>
        <el-button type="primary" size="small" :icon="Plus" @click="newConversation" round plain>新对话</el-button>
      </div>
      <div class="sidebar-search" v-if="conversations.length > 1">
        <el-input v-model="searchKeyword" placeholder="搜索对话..." size="small" clearable :prefix-icon="Search" />
      </div>
      <div class="sidebar-list" v-loading="loadingConvs">
        <div v-for="c in filteredConversations" :key="c.id"
          :class="['sidebar-item', { active: c.id === currentConvId }]"
          @click="switchConversation(c)">
          <div class="sidebar-item-content">
            <div class="sidebar-item-title">{{ c.title }}</div>
            <div class="sidebar-item-meta">
              <el-icon :size="12"><ChatDotRound /></el-icon>
              {{ c.message_count }} 条消息
              <span class="meta-dot">·</span>
              {{ formatTimeShort(c.updated_at) }}
            </div>
          </div>
          <el-button class="sidebar-item-del" :icon="Delete" size="small" text @click.stop="deleteConversation(c)" />
        </div>
        <el-empty v-if="!loadingConvs && !conversations.length" :image-size="40" description="暂无对话记录" />
        <el-empty v-if="!loadingConvs && conversations.length && !filteredConversations.length" :image-size="32" description="未找到匹配的对话" />
      </div>
    </div>

    <div class="chat-page">
      <div class="chat-header">
        <div class="chat-header-info">
          <div class="chat-header-icon"><el-icon :size="20"><ChatDotRound /></el-icon></div>
          <div class="chat-header-text">
            <span class="chat-header-title">{{ currentConvTitle || 'AI 问答' }}</span>
            <span v-if="currentConvId" class="chat-header-sub">继续对话</span>
          </div>
        </div>
        <div class="chat-header-actions">
          <el-select v-model="selectedCourseId" placeholder="全部课程" clearable size="small" style="width:170px" @change="onCourseChange">
            <el-option v-for="c in courseList" :key="c.id" :label="c.course_name" :value="c.id" />
          </el-select>
          <el-tooltip content="清空当前对话消息" placement="bottom">
            <el-button text :icon="Delete" @click="clearChat" :disabled="!messages.length" />
          </el-tooltip>
        </div>
      </div>

      <div class="chat-body" ref="chatRef">
        <div v-if="!messages.length" class="chat-empty">
          <div class="empty-graphic">
            <div class="empty-orb"></div>
            <div class="empty-orb orb-2"></div>
            <div class="empty-orb orb-3"></div>
            <el-icon :size="48" color="#fff" class="empty-icon-inner"><ChatDotRound /></el-icon>
          </div>
          <p class="empty-title">有什么可以帮你的？</p>
          <p class="empty-desc">我是 AI 课程助手，基于课件内容为你解答问题</p>
          <div class="empty-hints">
            <button v-for="hint in hints" :key="hint" class="hint-chip" @click="sendHint(hint)">
              <el-icon :size="14"><ChatLineRound /></el-icon>
              {{ hint }}
            </button>
          </div>
        </div>

        <div v-for="(msg, i) in messages" :key="i" :class="['msg-row', msg.role]">
          <div class="msg-avatar">
            <div v-if="msg.role === 'user'" class="avatar-user">我</div>
            <div v-else class="avatar-ai"><el-icon :size="18"><Promotion /></el-icon></div>
          </div>
          <div class="msg-content">
            <div class="msg-role">{{ msg.role === 'user' ? '你' : 'AI 助手' }}</div>
            <div class="msg-bubble">
              <div class="msg-text" v-html="msg.displayContent || msg.content"></div>
              <div v-if="msg.sources?.length" class="msg-sources">
                <div class="source-title"><el-icon :size="12"><Link /></el-icon> 参考来源</div>
                <div v-for="(s, j) in msg.sources" :key="j" class="source-item">
                  <el-tooltip placement="top">
                    <template #content>
                      <div>课件：{{ s.courseware_title || '未知课件' }}</div>
                      <div v-if="s.page_ref">第 {{ s.page_ref }} 页</div>
                    </template>
                    <el-tag size="small" round color="#e8f4fd" style="color:#1d7ab8;border:none;cursor:pointer">
                      <template v-if="s.heading && s.page_ref">{{ s.heading }}(第{{ s.page_ref }}页)</template>
                      <template v-else-if="s.page_ref">{{ s.courseware_title || '' }} · 第{{ s.page_ref }}页</template>
                      <template v-else-if="s.heading">{{ s.heading }}</template>
                      <template v-else>片段 #{{ s.chunk_index }}</template>
                    </el-tag>
                  </el-tooltip>
                </div>
              </div>
              <div v-if="msg.role === 'assistant'" class="msg-actions">
                <button class="msg-action-btn" :class="{ liked: msg.feedback === 'like' }"
                  @click="sendFeedback(msg, 'like')" title="有用">
                  <el-icon :size="14"><CircleCheck /></el-icon>
                </button>
                <button class="msg-action-btn" :class="{ disliked: msg.feedback === 'dislike' }"
                  @click="sendFeedback(msg, 'dislike')" title="无用">
                  <el-icon :size="14"><CloseBold /></el-icon>
                </button>
                <button class="msg-action-btn" @click="copyMessage(msg.content)" title="复制回答">
                  <el-icon :size="14"><DocumentCopy /></el-icon>
                </button>
              </div>
            </div>
          </div>
        </div>

        <div v-if="streaming" class="msg-row assistant">
          <div class="msg-avatar"><div class="avatar-ai"><el-icon :size="18"><Promotion /></el-icon></div></div>
          <div class="msg-content">
            <div class="msg-role">AI 助手</div>
            <div class="msg-bubble">
              <div class="streaming-text">
                <span v-html="renderedStream"></span><span class="cursor-blink">|</span>
              </div>
            </div>
          </div>
        </div>

        <div v-if="!streaming && loading" class="msg-row assistant">
          <div class="msg-avatar"><div class="avatar-ai"><el-icon :size="18"><Promotion /></el-icon></div></div>
          <div class="msg-content">
            <div class="msg-role">AI 助手</div>
            <div class="msg-bubble">
              <div class="thinking-dots"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div>
            </div>
          </div>
        </div>
      </div>

      <div class="chat-input-bar">
        <div class="input-wrapper">
          <textarea v-model="inputText" class="chat-textarea"
            placeholder="输入你的问题..."
            :disabled="streaming || loading"
            @keydown.enter.exact.prevent="sendMessage"
            rows="1" ref="textareaRef"></textarea>
          <button class="send-btn"
            :disabled="!inputText.trim() || streaming || loading"
            @click="sendMessage">
            <el-icon :size="18"><Position /></el-icon>
          </button>
        </div>
        <div class="input-footer">
          <span class="input-hint">Enter 发送 · Shift+Enter 换行</span>
          <span v-if="selectedCourseId" class="input-tag">
            <el-icon :size="12"><Notebook /></el-icon>
            {{ courseList.find(c => c.id === selectedCourseId)?.course_name || '已选课程' }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, computed, onMounted, nextTick, watch } from "vue"
import { useRoute } from "vue-router"
import {
  ChatDotRound, ChatSquare, ChatLineRound,
  Promotion, Delete, Position, Plus, Search,
  Fold, Expand, Link, DocumentCopy, Notebook, CircleCheck, CloseBold
} from "@element-plus/icons-vue"
import { marked } from "marked"
import request from "../api/request"
import { listCourses } from "../api/course"

marked.setOptions({ breaks: true, gfm: true })

function renderMarkdown(text) {
  if (!text) return ""
  return marked.parse(text)
}

const route = useRoute()
const chatRef = ref(null)
const textareaRef = ref(null)
const inputText = ref("")
const messages = ref([])
const loading = ref(false)
const streaming = ref(false)
const streamBuffer = ref("")
const courseList = ref([])
const selectedCourseId = ref(null)
const sidebarOpen = ref(true)
const searchKeyword = ref("")
const conversations = ref([])
const currentConvId = ref(null)
const currentConvTitle = ref("")
const loadingConvs = ref(false)

const hints = [
  "这门课主要讲什么？",
  "帮我梳理第二章的知识点",
  "用通俗的方式解释一下过拟合",
  "这章的重点和难点分别是什么？"
]

const filteredConversations = computed(() => {
  if (!searchKeyword.value) return conversations.value
  const kw = searchKeyword.value.toLowerCase()
  return conversations.value.filter(c => c.title.toLowerCase().includes(kw))
})

const renderedStream = computed(() => {
  if (!streamBuffer.value) return ""
  try { return marked.parse(streamBuffer.value) }
  catch { return streamBuffer.value }
})

function formatTimeShort(dateStr) {
  if (!dateStr) return ""
  try {
    const d = new Date(dateStr), now = new Date(), diff = now - d
    if (diff < 60000) return "刚刚"
    if (diff < 3600000) return Math.floor(diff / 60000) + "分钟前"
    if (diff < 86400000) return Math.floor(diff / 3600000) + "小时前"
    if (diff < 172800000) return "昨天"
    return String(d.getMonth() + 1).padStart(2, "0") + "/" + String(d.getDate()).padStart(2, "0")
  } catch { return dateStr?.slice(5, 10) || "" }
}

onMounted(async () => {
  const urlCourseId = route.params.courseId || route.query.course_id
  if (urlCourseId) selectedCourseId.value = Number(urlCourseId)
  try { const res = await listCourses(); courseList.value = res.data?.courses || [] }
  catch { courseList.value = [] }
  await fetchConversations()
})

async function fetchConversations() {
  loadingConvs.value = true
  try {
    const res = await request.get("/api/chat/conversations")
    conversations.value = res.data?.conversations || []
  } catch { conversations.value = [] }
  loadingConvs.value = false
}

async function newConversation() {
  currentConvId.value = null; currentConvTitle.value = ""
  messages.value = []; streamBuffer.value = ""; streaming.value = false
}

async function switchConversation(conv) {
  currentConvId.value = conv.id; currentConvTitle.value = conv.title; messages.value = []
  try {
    const res = await request.get("/api/chat/conversations/" + conv.id)
    if (res.data?.messages) {
      messages.value = res.data.messages.map(m => ({
        role: m.role, content: m.content,
        displayContent: m.role === "assistant" ? renderMarkdown(m.content) : m.content,
        sources: m.referenced_chunks || [],
        feedback: null,
        messageId: m.id,
      }))
    }
    selectedCourseId.value = res.data.course_id || null
  } catch {}
  await nextTick(); scrollDown()
}

async function deleteConversation(conv) {
  try {
    await request.delete("/api/chat/conversations/" + conv.id)
    if (currentConvId.value === conv.id) {
      currentConvId.value = null; currentConvTitle.value = ""; messages.value = []
    }
    await fetchConversations()
  } catch {}
}

function onCourseChange() {}

function autoResizeTextarea() {
  nextTick(() => {
    const el = textareaRef.value
    if (el) { el.style.height = "auto"; el.style.height = Math.min(el.scrollHeight, 120) + "px" }
  })
}
watch(inputText, () => autoResizeTextarea())

async function sendMessage() {
  const text = inputText.value.trim()
  if (!text || streaming.value || loading.value) return
  inputText.value = ""
  messages.value.push({ role: "user", content: text })
  loading.value = true; scrollDown()

  try {
    const payload = { message: text, course_id: selectedCourseId.value || null }
    if (currentConvId.value) payload.conversation_id = currentConvId.value
    const res = await request.post("/api/chat", payload)
    loading.value = false

    if (res.data?.conversation_id) {
      currentConvId.value = res.data.conversation_id
      currentConvTitle.value = res.data.conversation_title || currentConvTitle.value
    }

    const answer = res.data?.answer || res.answer || "暂无回答"
    const sources = res.data?.sources || []

    streamBuffer.value = ""; streaming.value = true
    autoResizeTextarea(); scrollDown()

    const chars = answer.split(""); let idx = 0
    const interval = setInterval(() => {
      if (idx < chars.length) { streamBuffer.value += chars[idx]; idx++; scrollDown() }
      else {
        clearInterval(interval)
        streaming.value = false
        messages.value.push({
          role: "assistant", content: answer,
          displayContent: renderMarkdown(answer), sources,
          feedback: null, messageId: res.data?.message_id || null
        })
        streamBuffer.value = ""; scrollDown()
        fetchConversations()
      }
    }, 30)
  } catch {
    loading.value = false
    messages.value.push({ role: "assistant", content: "抱歉，暂时无法回答，请稍后再试。", sources: [] })
    scrollDown()
  }
}

async function sendFeedback(msg, type) {
  if (msg.feedback === type) { msg.feedback = null; return }
  msg.feedback = type
  try {
    await request.post("/api/chat/feedback", {
      message_id: msg.messageId,
      type: type,
    })
  } catch { msg.feedback = null }
}

function copyMessage(text) { navigator.clipboard.writeText(text).catch(() => {}) }
function sendHint(hint) { inputText.value = hint; sendMessage() }
function clearChat() { messages.value = []; streamBuffer.value = ""; streaming.value = false }
function scrollDown() { nextTick(() => chatRef.value?.scrollTo({ top: chatRef.value.scrollHeight, behavior: "smooth" })) }
</script>
<style scoped>
.chat-layout { display: flex; height: calc(100vh - 100px); gap: 12px; position: relative; transition: all 0.3s ease; }
.sidebar-toggle { position: absolute; left: -8px; top: 50%; transform: translateY(-50%); z-index: 10; width: 24px; height: 48px; border-radius: 0 8px 8px 0; border: 1px solid #e4e7ed; border-left: none; background: #fff; cursor: pointer; display: flex; align-items: center; justify-content: center; color: #909399; box-shadow: 1px 0 4px rgba(0,0,0,0.06); transition: all 0.2s; }
.sidebar-toggle:hover { color: #409eff; background: #f5f7fa; }
.sidebar-collapsed .sidebar-toggle { left: 0; border-radius: 0 8px 8px 0; }
.chat-sidebar { width: 280px; min-width: 280px; background: #fff; border-radius: 10px; display: flex; flex-direction: column; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.05); transition: all 0.3s ease; }
.sidebar-collapsed .chat-sidebar { width: 0; min-width: 0; margin-left: -280px; opacity: 0; }
.sidebar-header { display: flex; align-items: center; justify-content: space-between; padding: 16px 16px 12px; flex-shrink: 0; }
.sidebar-header-left { display: flex; align-items: center; gap: 8px; }
.sidebar-title { font-size: 16px; font-weight: 600; color: #1d2129; }
.sidebar-search { padding: 0 12px 8px; flex-shrink: 0; }
.sidebar-search :deep(.el-input__wrapper) { border-radius: 8px; background: #f5f7fa; box-shadow: none !important; }
.sidebar-search :deep(.el-input__wrapper.is-focus) { background: #e8f4fd; }
.sidebar-list { flex: 1; overflow-y: auto; padding: 4px 8px 12px; }
.sidebar-list::-webkit-scrollbar { width: 4px; }
.sidebar-list::-webkit-scrollbar-thumb { background: #e4e7ed; border-radius: 2px; }
.sidebar-item { display: flex; align-items: center; padding: 10px 12px; border-radius: 8px; cursor: pointer; margin-bottom: 2px; position: relative; transition: all 0.15s ease; gap: 8px; }
.sidebar-item:hover { background: #f5f7fa; }
.sidebar-item.active { background: #ecf5ff; }
.sidebar-item.active .sidebar-item-title { color: #409eff; }
.sidebar-item-content { flex: 1; min-width: 0; }
.sidebar-item-title { font-size: 14px; font-weight: 500; color: #1d2129; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; line-height: 1.4; }
.sidebar-item-meta { font-size: 12px; color: #a8abb2; margin-top: 3px; display: flex; align-items: center; gap: 3px; }
.meta-dot { color: #d0d5dd; }
.sidebar-item-del { opacity: 0; transition: opacity 0.15s; flex-shrink: 0; color: #c0c4cc; }
.sidebar-item-del:hover { color: #f56c6c !important; }
.sidebar-item:hover .sidebar-item-del { opacity: 1; }
.chat-page { flex: 1; display: flex; flex-direction: column; background: #fff; border-radius: 10px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.05); position: relative; }
.chat-header { display: flex; align-items: center; justify-content: space-between; padding: 14px 20px; border-bottom: 1px solid #f2f3f5; flex-shrink: 0; background: #fff; }
.chat-header-info { display: flex; align-items: center; gap: 10px; }
.chat-header-icon { width: 32px; height: 32px; background: linear-gradient(135deg, #409eff, #337ecc); border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #fff; position: relative; box-shadow: 0 0 0 1px rgba(255,255,255,0.3), 0 2px 12px rgba(64,158,255,0.3); transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1); }
.chat-header-icon::before { content: ''; position: absolute; inset: -3px; border-radius: 11px; background: linear-gradient(135deg, #4a7cff, #7c5ce7, #4a7cff); background-size: 300% 300%; animation: hdr-icon-ring 3s ease infinite; z-index: -1; }
.chat-header:hover .chat-header-icon { transform: scale(1.1) rotate(-5deg); box-shadow: 0 0 0 2px rgba(255,255,255,0.5), 0 4px 20px rgba(64,158,255,0.4); }
.chat-header-text { display: flex; flex-direction: column; }
.chat-header-title { font-size: 17px; font-weight: 600; color: #1d2129; line-height: 1.3; }
.chat-header-sub { font-size: 12px; color: #a8abb2; line-height: 1.2; }
.chat-header-actions { display: flex; align-items: center; gap: 8px; }
.chat-body { flex: 1; overflow-y: auto; padding: 24px 32px; scroll-behavior: smooth; background: #fafbfc; }
.chat-body::-webkit-scrollbar { width: 6px; }
.chat-body::-webkit-scrollbar-thumb { background: #e4e7ed; border-radius: 3px; }
.chat-body::-webkit-scrollbar-track { background: transparent; }
.chat-empty { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; padding: 40px; text-align: center; }
.empty-graphic { position: relative; width: 120px; height: 120px; margin-bottom: 24px; display: flex; align-items: center; justify-content: center; }
.empty-orb { position: absolute; width: 100%; height: 100%; border-radius: 50%; background: radial-gradient(circle at 30% 30%, #e8f4fd, #d0e8ff); opacity: 0.5; animation: orb-float 4s ease-in-out infinite; }
.orb-2 { width: 80%; height: 80%; background: radial-gradient(circle at 70% 70%, #ecf5ff, #d4eaff); animation-delay: -1.5s; opacity: 0.6; }
.orb-3 { width: 60%; height: 60%; background: radial-gradient(circle at 50% 50%, #fff, #e8f4fd); animation-delay: -3s; opacity: 0.8; }
.empty-icon-inner { position: relative; z-index: 1; filter: drop-shadow(0 2px 4px rgba(64,158,255,0.3)); }
@keyframes orb-float { 0%,100% { transform: translateY(0) scale(1); } 50% { transform: translateY(-8px) scale(1.05); } }
.empty-title { font-size: 22px; font-weight: 600; color: #1d2129; margin: 0 0 8px; }
.empty-desc { font-size: 15px; color: #86909c; margin: 0 0 28px; line-height: 1.5; }
.empty-hints { display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; }
.hint-chip { display: inline-flex; align-items: center; gap: 6px; padding: 10px 16px; background: #fff; border: 1px solid #e4e7ed; border-radius: 10px; font-size: 14px; color: #4e5969; cursor: pointer; transition: all 0.2s ease; font-family: inherit; }
.hint-chip:hover { border-color: #409eff; color: #409eff; box-shadow: 0 2px 8px rgba(64,158,255,0.12); transform: translateY(-1px); }
.msg-row { display: flex; gap: 12px; margin-bottom: 24px; animation: msg-in 0.3s ease-out; }
@keyframes msg-in { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }
.msg-row.user { flex-direction: row-reverse; }
.avatar-user { width: 36px; height: 36px; border-radius: 10px; background: linear-gradient(135deg, #409eff, #2468cc); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 600; }
.avatar-ai { width: 36px; height: 36px; border-radius: 10px; background: linear-gradient(135deg, #52c41a, #389e0d); color: #fff; display: flex; align-items: center; justify-content: center; }
.msg-content { max-width: 68%; min-width: 0; }
.msg-row.user .msg-content { display: flex; align-items: flex-end; }
.msg-role { font-size: 13px; color: #a8abb2; margin-bottom: 6px; font-weight: 500; }
.msg-bubble { padding: 14px 18px; border-radius: 12px; font-size: 15px; line-height: 1.7; word-break: break-word; position: relative; }
.msg-row.user .msg-bubble { background: linear-gradient(135deg, #409eff, #337ecc); color: #fff; border-bottom-right-radius: 4px; box-shadow: 0 2px 8px rgba(64,158,255,0.2); }
.msg-row.assistant .msg-bubble { background: #fff; color: #1d2129; border-bottom-left-radius: 4px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); border: 1px solid #f0f0f0; }
.msg-text { line-height: 1.8; }
.msg-text :deep(h1),.msg-text :deep(h2),.msg-text :deep(h3),.msg-text :deep(h4),.msg-text :deep(h5),.msg-text :deep(h6) { margin: 14px 0 6px; font-weight: 600; line-height: 1.4; }
.msg-text :deep(h1) { font-size: 20px; }
.msg-text :deep(h2) { font-size: 19px; }
.msg-text :deep(h3) { font-size: 18px; }
.msg-text :deep(p) { margin: 4px 0 6px; }
.msg-text :deep(ul),.msg-text :deep(ol) { padding-left: 20px; margin: 4px 0 6px; }
.msg-text :deep(li) { margin: 2px 0; }
.msg-text :deep(strong) { font-weight: 600; }
.msg-text :deep(code) { background: #f2f3f5; padding: 2px 6px; border-radius: 4px; font-size: 14px; font-family: 'Consolas','Menlo',monospace; color: #e83e8c; }
.msg-row.assistant .msg-text :deep(code) { background: #f0f2f5; }
.msg-text :deep(pre) { background: #f6f8fa; border: 1px solid #eef0f2; border-radius: 8px; padding: 12px 16px; overflow-x: auto; margin: 8px 0; }
.msg-text :deep(pre code) { background: none; padding: 0; color: #303133; font-size: 13px; line-height: 1.6; }
.msg-text :deep(blockquote) { border-left: 3px solid #409eff; padding: 6px 14px; margin: 8px 0; background: #f6faff; border-radius: 0 6px 6px 0; color: #4e5969; }
.msg-text :deep(table) { border-collapse: collapse; margin: 8px 0; font-size: 14px; width: 100%; }
.msg-text :deep(th),.msg-text :deep(td) { border: 1px solid #e8e8e8; padding: 8px 12px; text-align: left; }
.msg-text :deep(th) { background: #f6f8fa; font-weight: 600; }
.msg-text :deep(hr) { border: none; border-top: 1px solid #eef0f2; margin: 12px 0; }
.msg-text :deep(a) { color: #409eff; text-decoration: none; }
.msg-text :deep(a:hover) { text-decoration: underline; }
.msg-sources { margin-top: 12px; padding-top: 10px; border-top: 1px solid #f0f0f0; }
.source-title { font-size: 12px; color: #a8abb2; margin-bottom: 6px; font-weight: 500; display: flex; align-items: center; gap: 4px; }
.source-item { display: inline-block; margin: 2px; }
.msg-actions { margin-top: 8px; display: flex; gap: 4px; opacity: 0; transition: opacity 0.2s; }
.msg-row.assistant:hover .msg-actions { opacity: 1; }
.msg-action-btn { width: 28px; height: 28px; border-radius: 6px; border: none; background: transparent; color: #a8abb2; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.15s; }
.msg-action-btn:hover { background: #f0f2f5; color: #409eff; }
.msg-action-btn.liked { color: #67c23a; background: #f0f9eb; }
.msg-action-btn.disliked { color: #f56c6c; background: #fef0f0; }
.chat-input-bar { flex-shrink: 0; padding: 16px 20px 14px; border-top: 1px solid #f2f3f5; background: #fff; }
.input-wrapper { display: flex; align-items: flex-end; gap: 8px; background: #f5f7fa; border-radius: 12px; padding: 8px 8px 8px 16px; border: 1px solid #e4e7ed; transition: all 0.2s; }
.input-wrapper:focus-within { border-color: #409eff; box-shadow: 0 0 0 2px rgba(64,158,255,0.12); background: #fff; }
.chat-textarea { flex: 1; border: none; outline: none; background: transparent; font-size: 15px; line-height: 1.5; color: #1d2129; resize: none; max-height: 120px; padding: 4px 0; font-family: inherit; }
.chat-textarea::placeholder { color: #c0c4cc; }
.chat-textarea:disabled { cursor: not-allowed; }
.send-btn { width: 38px; height: 38px; border-radius: 10px; border: none; background: linear-gradient(135deg, #409eff, #337ecc); color: #fff; cursor: pointer; display: flex; align-items: center; justify-content: center; flex-shrink: 0; transition: all 0.2s; box-shadow: 0 2px 6px rgba(64,158,255,0.25); }
.send-btn:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(64,158,255,0.35); }
.send-btn:active:not(:disabled) { transform: translateY(0); }
.send-btn:disabled { background: #d0d5dd; cursor: not-allowed; box-shadow: none; }
.input-footer { display: flex; align-items: center; justify-content: space-between; margin-top: 6px; padding: 0 4px; }
.input-hint { font-size: 12px; color: #c0c4cc; }
.input-tag { font-size: 12px; color: #409eff; display: flex; align-items: center; gap: 4px; }
.streaming-text { font-size: 15px; line-height: 1.8; color: #1d2129; }
.cursor-blink { animation: blink 0.8s infinite; color: #409eff; font-weight: bold; margin-left: 1px; }
@keyframes blink { 0%,100% { opacity: 1; } 50% { opacity: 0; } }
.thinking-dots { display: flex; gap: 6px; padding: 4px 0; }
.thinking-dots .dot { width: 8px; height: 8px; background: #c0c4cc; border-radius: 50%; animation: bounce 1.2s infinite; }
.thinking-dots .dot:nth-child(1) { animation-delay: 0s; }
.thinking-dots .dot:nth-child(2) { animation-delay: 0.2s; }
.thinking-dots .dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce { 0%,60%,100% { transform: translateY(0); opacity: 0.3; } 30% { transform: translateY(-6px); opacity: 1; } }
@keyframes hdr-icon-ring { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
</style>
