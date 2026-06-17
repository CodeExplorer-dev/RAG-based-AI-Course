<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <div class="login-logo">
          <el-icon :size="36" color="#409eff"><ChatDotRound /></el-icon>
        </div>
        <h2 class="login-title">AI 课程答疑系统</h2>
        <p class="login-subtitle">{{ isRegister ? '创建新账号' : '欢迎回来' }}</p>
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
          <el-input v-model="form.username" placeholder="用户名" :prefix-icon="User" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码" :prefix-icon="Lock" show-password />
        </el-form-item>
        <template v-if="isRegister">
          <el-form-item prop="confirmPassword">
            <el-input v-model="form.confirmPassword" type="password" placeholder="确认密码" :prefix-icon="Lock" show-password />
          </el-form-item>
          <el-form-item prop="role">
            <el-select v-model="form.role" placeholder="选择角色" style="width: 100%">
              <el-option label="学生" value="student" />
              <el-option label="教师" value="teacher" />
              <el-option label="管理员" value="admin" />
            </el-select>
          </el-form-item>
        </template>
        <el-form-item>
          <el-button type="primary" native-type="submit" :loading="loading" class="login-btn" round>
            {{ isRegister ? '注册' : '登录' }}
          </el-button>
        </el-form-item>
      </el-form>
      <div class="login-footer">
        <span class="footer-text">{{ isRegister ? '已有账号：' : '没有账号：' }}</span>
        <el-button link @click="isRegister = !isRegister">
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
    {
      validator: (_, val) => val === form.password ? Promise.resolve() : Promise.reject(new Error('两次密码不一致')),
      trigger: 'blur'
    }
  ]
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
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f4ff;
}
.login-card {
  width: 400px;
  padding: 40px 36px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 8px 60px rgba(0, 0, 0, 0.12);
}
.login-header { text-align: center; margin-bottom: 32px; }
.login-logo { margin-bottom: 12px; }
.login-title { font-size: 28px; font-weight: 700; color: #1d2129; margin: 0 0 6px; letter-spacing: 0; }
.login-subtitle { font-size: 18px; color: #86909c; margin: 0; }
.login-form { margin-bottom: 8px; }
.login-btn { width: 100%; height: 46px; font-size: 18px; letter-spacing: 0; }
.login-footer {
  text-align: center;
  font-size: 18px;
  color: #86909c;
}
.footer-text { margin-right: 2px; }
</style>
