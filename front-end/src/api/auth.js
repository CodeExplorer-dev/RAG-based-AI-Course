import request from './request'

/** 用户注册 */
export function register(data) {
  return request.post('/api/auth/register', data)
}

/** 用户登录，返回 { access_token, refresh_token, user } */
export function login(data) {
  return request.post('/api/auth/login', data)
}

/** 刷新 access_token */
export function refreshToken() {
  return request.post('/api/auth/refresh')
}
