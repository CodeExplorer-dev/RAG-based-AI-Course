import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login as loginApi, register as registerApi } from '../api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || 'null'))

  function setToken(val) {
    token.value = val
    localStorage.setItem('token', val)
  }

  function setUserInfo(info) {
    userInfo.value = info
    localStorage.setItem('userInfo', JSON.stringify(info))
  }

  async function login(credentials) {
    const res = await loginApi(credentials)
    // 后端返回格式：{ code, message, data: { access_token, refresh_token, user } }
    const d = res.data
    setToken(d.access_token)
    setUserInfo(d.user)
    return d
  }

  async function register(data) {
    return await registerApi(data)
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
  }

  return { token, userInfo, login, register, logout, setToken, setUserInfo }
})
