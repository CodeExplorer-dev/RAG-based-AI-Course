<template>
  <div class="coming-soon">
    <el-icon :size="64" color="#c0c4cc"><Clock /></el-icon>
    <h3>{{ title }}</h3>
    <p>该功能正在开发中，敬请期待</p>
  </div>
</template>

<script setup>
import { Clock } from '@element-plus/icons-vue'

defineProps({
  title: { type: String, default: '功能开发中' }
})
</script>

<style scoped>
.coming-soon {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}
.coming-soon h3 {
  font-size: 22px;
  color: #606266;
  margin: 20px 0 8px;
}
.coming-soon p {
  font-size: 16px;
  color: #909399;
  margin: 0;
}
</style>
