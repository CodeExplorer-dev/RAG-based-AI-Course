import request from "./request"

/** 获取当前用户的 AI 问答会话列表 */
export function listConversations() {
  return request.get("/api/chat/conversations")
}

/** 获取会话详情（含消息列表） */
export function getConversation(convId) {
  return request.get(`/api/chat/conversations/${convId}`)
}

/** 删除会话 */
export function deleteConversation(convId) {
  return request.delete(`/api/chat/conversations/${convId}`)
}
