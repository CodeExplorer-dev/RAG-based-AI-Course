/** 通知相关 API */
import request from "./request"

/** 获取通知列表 */
export function listNotifications() {
  return request.get("/api/notifications")
}

/** 获取未读通知数量 */
export function getUnreadCount() {
  return request.get("/api/notifications/unread-count")
}

/** 标记单条通知为已读 */
export function markRead(id) {
  return request.put(`/api/notifications/${id}/read`)
}

/** 标记全部为已读 */
export function markAllRead() {
  return request.put("/api/notifications/read-all")
}
