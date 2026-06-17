import request from './request'

/** 获取当前用户信息 */
export function getProfile() {
  return request.get('/api/user/me')
}

/** 更新用户信息（email, password） */
export function updateProfile(data) {
  return request.put('/api/user/me', data)
}
