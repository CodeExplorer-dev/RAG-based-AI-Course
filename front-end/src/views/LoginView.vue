<template>
  <div class="login-page">
    <div class="login-bg">
      <div class="bg-orb orb-1"></div>
      <div class="bg-orb orb-2"></div>
      <div class="bg-orb orb-3"></div>
      <div class="bg-grid"></div>
    </div>
    <div class="login-card" :class="{ 'card-register': isRegister }">
      <div class="login-header">
        <div class="login-logo">
          <el-icon :size="40" color="#fff"><ChatDotRound /></el-icon>
        </div>
        <h2 class="login-title">AI 课程答疑系统</h2>
        <p class="login-subtitle">{{ isRegister ? '创建新账号，开始智能学习之旅' : '欢迎回来，继续你的学习之旅' }}</p>
      </div>
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="0"
        size="large"
        class="login-form"
        @submit.prevent="handleSubmit"
      >
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" :prefix-icon="User" class="login-input" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码" :prefix-icon="Lock" show-password class="login-input" />
        </el-form-item>
        <template v-if="isRegister">
          <el-form-item prop="confirmPassword">
            <el-input v-model="form.confirmPassword" type="password" placeholder="确认密码" :prefix-icon="Lock" show-password class="login-input" />
          </el-form-item>
          <el-form-item prop="role">
            <el-select v-model="form.role" placeholder="选择角色" class="login-input">
              <el-option label="学生" value="student" />
              <el-option label="教师" value="teacher" />
              <el-option label="管理员" value="admin" />
            </el-select>
          </el-form-item>
        </template>
        <el-form-item>
          <el-button type="primary" native-type="submit" :loading="loading" class="login-btn">
            {{ isRegister ? '注册' : '登录' }}
          </el-button>
        </el-form-item>
      </el-form>
      <div class="login-footer">
        <span class="footer-text">{{ isRegister ? '已有账号？' : '没有账号？' }}</span>
        <el-button link class="switch-btn" @click="switchMode">
          {{ isRegister ? '去登录' : '去注册' }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, ChatDotRound } from '@element-plus/icons-vue'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref(null)
const isRegister = ref(false)
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
  confirmPassword: '',
  role: 'student'
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: (_, val) => val === form.password ? Promise.resolve() : Promise.reject(new Error('两次密码不一致')), trigger: 'blur' }
  ]
}

function switchMode() {
  isRegister.value = !isRegister.value
  formRef.value?.clearValidate()
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    if (isRegister.value) {
      await userStore.register({ username: form.username, password: form.password, role: form.role })
      ElMessage.success('注册成功，请登录')
      isRegister.value = false
    } else {
      await userStore.login({ username: form.username, password: form.password })
      ElMessage.success('登录成功')
      const role = userStore.userInfo?.role
      if (role === 'admin') router.push('/admin/dashboard')
      else if (role === 'teacher') router.push('/teacher/dashboard')
      else router.push('/courses')
    }
  } finally { loading.value = false }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #0a1628 0%, #0d2847 30%, #1a1a3e 60%, #0d1628 100%);
}

/* Background orbs */
.login-bg { position: absolute; inset: 0; pointer-events: none; overflow: hidden; }
.bg-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.3;
  animation: orb-drift 20s ease-in-out infinite;
}
.orb-1 {
  width: 500px; height: 500px;
  background: radial-gradient(circle, #5b8def, #409eff);
  top: -15%; left: -10%;
  animation-delay: 0s;
}
.orb-2 {
  width: 400px; height: 400px;
  background: radial-gradient(circle, #7c3aed, #5b8def);
  bottom: -10%; right: -8%;
  animation-delay: -7s;
}
.orb-3 {
  width: 300px; height: 300px;
  background: radial-gradient(circle, #3b82f6, #1a3a5c);
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  animation-delay: -14s;
}
.bg-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
  background-size: 60px 60px;
}
@keyframes orb-drift {
  0%, 100% { transform: translate(0, 0) scale(1); }
  25% { transform: translate(30px, -20px) scale(1.1); }
  50% { transform: translate(-20px, 30px) scale(0.95); }
  75% { transform: translate(20px, 10px) scale(1.05); }
}

/* Card */
.login-card {
  position: relative;
  width: 420px;
  padding: 44px 40px 36px;
  background: rgba(255,255,255,0.06);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-radius: 20px;
  border: 1px solid rgba(255,255,255,0.1);
  box-shadow: 0 20px 60px rgba(0,0,0,0.4);
  transition: all var(--transition-slow);
  z-index: 1;
}
.login-card:hover {
  box-shadow: 0 24px 80px rgba(64,158,255,0.15);
  border-color: rgba(91,141,239,0.3);
}
.login-header { text-align: center; margin-bottom: 36px; }
.login-logo {
  width: 72px;
  height: 72px;
  margin: 0 auto 16px;
  background: linear-gradient(135deg, #5b8def, #409eff);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 24px rgba(64,158,255,0.3);
}
.login-title { font-size: 26px; font-weight: 700; color: #f0f4ff; margin: 0 0 8px; letter-spacing: 0.5px; }
.login-subtitle { font-size: 15px; color: rgba(160,174,192,0.8); margin: 0; }

/* Form */
.login-form { margin-bottom: 4px; }
.login-input :deep(.el-input__wrapper) {
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.1);
  box-shadow: none;
  border-radius: 12px;
  padding: 4px 16px;
  transition: all var(--transition-fast);
}
.login-input :deep(.el-input__wrapper:hover) {
  border-color: rgba(91,141,239,0.4);
  background: rgba(255,255,255,0.1);
}
.login-input :deep(.el-input__wrapper.is-focus) {
  border-color: #5b8def;
  background: rgba(255,255,255,0.12);
  box-shadow: 0 0 0 3px rgba(91,141,239,0.12);
}
.login-input :deep(.el-input__inner) { color: #e8ecf4; height: 44px; }
.login-input :deep(.el-input__inner::placeholder) { color: rgba(160,174,192,0.5); }
.login-input :deep(.el-input__prefix-inner) { color: rgba(160,174,192,0.6); }
.login-input :deep(.el-select .el-input__wrapper) { height: 44px; }
.login-input :deep(.el-select-dropdown__item) { font-size: 14px; }

.login-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  letter-spacing: 1px;
  border-radius: 12px;
  background: linear-gradient(135deg, #5b8def, #409eff);
  border: none;
  box-shadow: 0 4px 16px rgba(64,158,255,0.3);
  transition: all var(--transition-fast);
  margin-top: 4px;
}
.login-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 24px rgba(64,158,255,0.4);
}
.login-btn:active { transform: translateY(0); }

.login-footer {
  text-align: center;
  font-size: 14px;
  color: rgba(160,174,192,0.7);
  padding-top: 8px;
}
.footer-text { margin-right: 4px; }
.switch-btn {
  color: #5b8def !important;
  font-size: 14px;
  font-weight: 500;
}
.switch-btn:hover { color: #409eff !important; }
</style>
