 <template>
   <div class="login-container">
     <div class="login-card">
       <h2 class="login-title">{{ isRegister ? '注册' : '登录' }}</h2>
       <el-form
         ref="formRef"
         :model="form"
         :rules="rules"
         label-width="0"
         size="large"
         @submit.prevent="handleSubmit"
       >
         <el-form-item prop="username">
           <el-input v-model="form.username" placeholder="用户名" :prefix-icon="User" />
         </el-form-item>
         <el-form-item prop="password">
           <el-input v-model="form.password" type="password" placeholder="密码" :prefix-icon="Lock" show-password />
         </el-form-item>
         <el-form-item v-if="isRegister" prop="confirmPassword">
           <el-input v-model="form.confirmPassword" type="password" placeholder="确认密码" :prefix-icon="Lock" show-password />
         </el-form-item>
         <el-form-item v-if="isRegister" prop="role">
           <el-select v-model="form.role" placeholder="选择角色" style="width: 100%">
             <el-option label="学生" value="student" />
             <el-option label="教师" value="teacher" />
           </el-select>
         </el-form-item>
         <el-form-item>
           <el-button type="primary" native-type="submit" :loading="loading" style="width: 100%">
             {{ isRegister ? '注册' : '登录' }}
           </el-button>
         </el-form-item>
       </el-form>
       <div class="login-footer">
         <el-button link @click="isRegister = !isRegister">
           {{ isRegister ? '已有账号？去登录' : '没有账号？去注册' }}
         </el-button>
       </div>
     </div>
   </div>
 </template>
 
 <script setup>
 import { ref, reactive } from 'vue'
 import { useRouter } from 'vue-router'
 import { ElMessage } from 'element-plus'
 import { User, Lock } from '@element-plus/icons-vue'
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
     { min: 6, message: '密码至少6位', trigger: 'blur' }
   ],
   confirmPassword: [
     { required: true, message: '请确认密码', trigger: 'blur' },
     {
       validator: (_, val, cb) =>
         val === form.password ? cb() : cb(new Error('两次密码不一致')),
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
       router.push('/')
     }
   } finally {
     loading.value = false
   }
 }
 </script>
 
 <style scoped>
 .login-container {
   height: 100vh;
   display: flex;
   align-items: center;
   justify-content: center;
   background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
 }
 .login-card {
   width: 400px;
   padding: 40px;
   background: #fff;
   border-radius: 8px;
   box-shadow: 0 4px 24px rgba(0, 0, 0, 0.15);
 }
 .login-title {
   text-align: center;
   margin-bottom: 30px;
   font-size: 24px;
   color: #333;
 }
 .login-footer {
   text-align: center;
   margin-top: 16px;
 }
 </style>
