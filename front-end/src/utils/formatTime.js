import dayjs from 'dayjs'
import utc from 'dayjs/plugin/utc'

dayjs.extend(utc)

/**
 * 将后端 UTC 时间字符串转为本地时间显示
 * 后端返回的时间格式为 'YYYY-MM-DD HH:mm:ss'，存储的是 UTC 时间（datetime.utcnow()）
 * 该函数将其标记为 UTC 后转为用户本地时区格式化
 *
 * @param {string} timeStr - 后端返回的时间字符串，格式 'YYYY-MM-DD HH:mm:ss'（UTC）
 * @param {string} format - 输出格式，默认 'YYYY-MM-DD HH:mm:ss'
 * @returns {string} 格式化后的本地时间字符串
 */
export function formatTime(timeStr, format = 'YYYY-MM-DD HH:mm:ss') {
  if (!timeStr) return '-'
  // 明确标记输入为 UTC，然后转为本地时间再格式化
  return dayjs.utc(timeStr).local().format(format)
}
