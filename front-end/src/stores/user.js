 import { defineStore } from 'pinia'
 import { ref } from 'vue'
 import request from '../api/request'
 
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
     const res = await request.post('/api/auth/login', credentials)
     setToken(res.token)
     setUserInfo(res.user)
     return res
   }
 
   async function register(data) {
     return await request.post('/api/auth/register', data)
   }
 
   function logout() {
     token.value = ''
     userInfo.value = null
     localStorage.removeItem('token')
     localStorage.removeItem('userInfo')
   }
 
   return { token, userInfo, login, register, logout, setToken, setUserInfo }
 })
