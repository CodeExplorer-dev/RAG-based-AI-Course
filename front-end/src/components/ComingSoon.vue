<template>
  <div class="coming-soon">
    <div class="cs-graphic">
      <div class="cs-orb"></div>
      <el-icon :size="52" color="#5b8def"><Clock /></el-icon>
    </div>
    <h3 class="cs-title">{{ title }}</h3>
    <p class="cs-desc">该功能正在开发中，敬请期待</p>
  </div>
</template>

<script setup>
import { Clock } from '@element-plus/icons-vue'
defineProps({ title: { type: String, default: '功能开发中' } })
</script>

<style scoped>
.coming-soon {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100px 20px;
  text-align: center;
}
.cs-graphic {
  position: relative;
  width: 100px;
  height: 100px;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.cs-orb {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, #e8f4fd, #d0e8ff);
  opacity: 0.4;
  animation: orb-pulse 3s ease-in-out infinite;
}
@keyframes orb-pulse {
  0%, 100% { transform: scale(1); opacity: 0.4; }
  50% { transform: scale(1.1); opacity: 0.6; }
}
.cs-title { font-size: 22px; font-weight: 600; color: var(--text-primary); margin: 0 0 8px; }
.cs-desc { font-size: 15px; color: var(--text-tertiary); margin: 0; }
</style>
