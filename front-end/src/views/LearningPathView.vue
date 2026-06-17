<template>
  <div class="lp-page">
    <div class="page-head">
      <h2 class="page-title">学习路径推荐</h2>
      <el-select v-model="selectedCourseId" placeholder="请选择课程" @change="loadPath" style="width: 220px" clearable>
        <el-option v-for="c in courseList" :key="c.id" :label="c.course_name" :value="c.id" />
      </el-select>
    </div>
    <template v-if="selectedCourseId">
      <div v-if="pathData" class="path-overview">
        <div class="progress-card">
          <span class="progress-label">{{ pathData.course_name }}</span>
          <el-progress :percentage="pathData.progress_percent" :stroke-width="10" striped />
          <span class="progress-text">已学习 {{ pathData.learnt_count }} / {{ pathData.total_courseware }} 个课件</span>
        </div>
        <div class="path-steps">
          <div v-for="step in pathData.steps" :key="step.step" class="step-card" :class="{ completed: step.step <= pathData.learnt_count }">
            <div class="step-indicator">
              <div class="step-circle" :class="{ active: step.step <= pathData.learnt_count }">
                <el-icon v-if="step.step <= pathData.learnt_count" :size="16" color="#fff"><Check /></el-icon>
                <span v-else>{{ step.step }}</span>
              </div>
              <div v-if="step.step < pathData.total_courseware" class="step-line"></div>
            </div>
            <div class="step-body">
              <div class="step-title">{{ step.title }}</div>
              <div class="step-meta">
                <el-tag size="small" type="info" round>{{ step.file_type }}</el-tag>
                <span class="step-time">{{ step.estimated_time }}</span>
              </div>
              <div v-if="step.key_points?.length" class="step-points">
                <el-tag v-for="(kp, i) in step.key_points" :key="i" size="small" type="warning" plain round>{{ kp }}</el-tag>
              </div>
            </div>
          </div>
        </div>
      </div>
      <el-empty v-else :image-size="80" description="暂无学习路径数据" />
    </template>
    <el-empty v-else :image-size="120" description="请先选择一个课程" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Check } from '@element-plus/icons-vue'
import { listCourses } from '../api/course'
import request from '../api/request'

const selectedCourseId = ref(null)
const courseList = ref([])
const pathData = ref(null)

onMounted(async () => {
  try {
    const res = await listCourses()
    courseList.value = res.data?.courses || []
  } catch { courseList.value = [] }
})

async function loadPath() {
  if (!selectedCourseId.value) return
  try {
    const res = await request.get('/api/learning-path/' + selectedCourseId.value)
    pathData.value = res.data
  } catch { pathData.value = null }
}
</script>

<style scoped>
.lp-page { padding: 0; }
.page-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
.page-title { font-size: 26px; font-weight: 600; color: #1d2129; margin: 0; }
.path-overview { max-width: 800px; }
.progress-card {
  background: #fff;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 32px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.progress-label { font-size: 20px; font-weight: 600; color: #1d2129; display: block; margin-bottom: 16px; }
.progress-text { font-size: 14px; color: #909399; margin-top: 8px; display: block; }
.path-steps { position: relative; }
.step-card {
  display: flex;
  gap: 20px;
  margin-bottom: 8px;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
  transition: box-shadow 0.2s;
}
.step-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.08); }
.step-card.completed { background: #f0f9eb; }
.step-indicator { display: flex; flex-direction: column; align-items: center; width: 32px; flex-shrink: 0; }
.step-circle {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  background: #e4e7ed;
  color: #909399;
}
.step-circle.active { background: #67c23a; color: #fff; }
.step-line {
  width: 2px;
  height: 100%;
  background: #e4e7ed;
  margin-top: 4px;
}
.step-body { flex: 1; }
.step-title { font-size: 18px; font-weight: 500; color: #1d2129; margin-bottom: 8px; }
.step-meta { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.step-time { font-size: 14px; color: #909399; }
.step-points { display: flex; gap: 6px; flex-wrap: wrap; }
</style>
