<template>
  <div class="kg-page">
    <div class="page-head">
      <h2 class="page-title">知识图谱</h2>
      <el-select v-model="selectedCourseId" placeholder="请选择课程" @change="loadGraph" style="width: 220px" clearable>
        <el-option v-for="c in courseList" :key="c.id" :label="c.course_name" :value="c.id" />
      </el-select>
    </div>
    <template v-if="selectedCourseId">
      <div class="kg-toolbar">
        <el-button :icon="ZoomIn" @click="zoomIn" circle />
        <el-button :icon="ZoomOut" @click="zoomOut" circle />
        <el-button :icon="Refresh" @click="fitView" circle />
        <span class="kg-info">节点: {{ nodes.length }} | 边: {{ edges.length }}</span>
      </div>
      <div class="kg-container" ref="kgContainer"></div>
    </template>
    <el-empty v-else :image-size="120" description="请先选择一个课程查看知识图谱" />
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { ZoomIn, ZoomOut, Refresh } from '@element-plus/icons-vue'
import { listCourses } from '../api/course'
import request from '../api/request'

const route = useRoute()
const kgContainer = ref(null)
const selectedCourseId = ref(null)
const courseList = ref([])
let network = null
const nodes = ref([])
const edges = ref([])

onMounted(async () => {
  try {
    const res = await listCourses()
    courseList.value = res.data?.courses || []
  } catch { courseList.value = [] }

  const urlCourseId = route.params.courseId
  if (urlCourseId) {
    selectedCourseId.value = Number(urlCourseId)
    await nextTick()
    await loadGraph()
  }
})

async function loadGraph() {
  if (!selectedCourseId.value) return
  try {
    const res = await request.get('/api/knowledge-graph/' + selectedCourseId.value)
    const data = res.data
    nodes.value = data?.nodes || []
    edges.value = data?.edges || []
    await nextTick()
    renderGraph()
  } catch { /* ignore */ }
}

function renderGraph() {
  if (!kgContainer.value) return
  const container = kgContainer.value

  const visNodes = new (window.vis.DataSet)(nodes.value.map(n => ({
    id: n.id,
    label: n.label,
    shape: n.type === 'course' ? 'star' : n.type === 'courseware' ? 'box' : 'ellipse',
    size: n.size || 20,
    color: {
      background: n.type === 'course' ? '#409eff' : n.type === 'courseware' ? '#67c23a' : '#e6a23c',
      border: n.type === 'course' ? '#337ecc' : n.type === 'courseware' ? '#5daf34' : '#d4880f',
      highlight: { background: '#ff6b6b', border: '#ee5a24' }
    },
    font: { size: 14, color: '#1d2129' }
  })))

  const visEdges = new (window.vis.DataSet)(edges.value.map(e => ({
    from: e.source,
    to: e.target,
    label: e.label,
    arrows: 'to',
    color: { color: '#c0c4cc', highlight: '#409eff' },
    font: { size: 11, color: '#909399', align: 'middle' },
    smooth: { type: 'curvedCW', roundness: 0.1 }
  })))

  const data = { nodes: visNodes, edges: visEdges }
  const options = {
    layout: { improvedLayout: true, hierarchical: { enabled: false } },
    physics: {
      solver: 'barnesHut',
      barnesHut: { gravitationalConstant: -3000, springLength: 200, springConstant: 0.04 },
      stabilization: { iterations: 200 }
    },
    interaction: { hover: true, tooltipDelay: 200, zoomView: true, dragView: true },
    edges: { smooth: true },
    nodes: { borderWidth: 2 }
  }

  network = new window.vis.Network(container, data, options)
  network.on('click', function(params) {
    if (params.nodes.length > 0) {
      const nodeId = params.nodes[0]
      const connected = network.getConnectedNodes(nodeId)
      network.selectNodes([nodeId, ...connected], false)
    }
  })
}

function zoomIn() { network && network.moveTo({ scale: network.getScale() * 1.2 }) }
function zoomOut() { network && network.moveTo({ scale: network.getScale() / 1.2 }) }
function fitView() { network && network.fit() }
</script>

<style scoped>
.kg-page { padding: 0; }
.page-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
.page-title { font-size: 26px; font-weight: 600; color: #1d2129; margin: 0; }
.kg-toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: #fff;
  border-radius: 8px;
  margin-bottom: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.kg-info { font-size: 14px; color: #909399; margin-left: 12px; }
.kg-container {
  width: 100%;
  height: calc(100vh - 280px);
  background: linear-gradient(135deg, #f8faff 0%, #f0f4ff 50%, #f5f0ff 100%);
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  overflow: hidden;
}
</style>
