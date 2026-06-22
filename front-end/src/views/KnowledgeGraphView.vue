<template>
  <div class="kg-page">
    <div class="page-head">
      <h2 class="page-title">知识图谱</h2>
      <div class="head-actions">
        <el-select v-model="selectedCourseId" placeholder="请选择课程" @change="loadGraph" style="width: 220px" clearable>
          <el-option v-for="c in courseList" :key="c.id" :label="c.course_name" :value="c.id" />
        </el-select>
        <el-button type="primary" :icon="Refresh" @click="rebuildGraph" :loading="building" :disabled="!selectedCourseId">
          重新生成图谱
        </el-button>
      </div>
    </div>
    <template v-if="selectedCourseId">
      <div class="kg-toolbar">
        <el-button :icon="ZoomIn" @click="zoomIn" circle />
        <el-button :icon="ZoomOut" @click="zoomOut" circle />
        <el-button :icon="Refresh" @click="fitView" circle />
        <span class="kg-info">节点: {{ nodes.length }} | 边: {{ edges.length }}</span>
      </div>
      <div class="kg-container" ref="kgContainer"></div>
      <!-- 图例 -->
      <div class="kg-legend">
        <div class="legend-title">图例</div>
        <div class="legend-section">
          <div class="legend-label">节点类型</div>
          <div class="legend-item"><span class="leg-node" style="background:#409eff;"></span> 课程</div>
          <div class="legend-item"><span class="leg-node" style="background:#1a3a5c;"></span> 一级知识点</div>
          <div class="legend-item"><span class="leg-node" style="background:#5b9bd5;"></span> 二/三级知识点</div>
          <div class="legend-item"><span class="leg-node" style="background:#67c23a;"></span> 课件</div>
        </div>
        <div class="legend-section">
          <div class="legend-label">关系类型</div>
          <div class="legend-item"><span class="leg-edge prereq"></span> 先修</div>
          <div class="legend-item"><span class="leg-edge contains"></span> 包含</div>
          <div class="legend-item"><span class="leg-edge related"></span> 相关</div>
          <div class="legend-item"><span class="leg-edge extends"></span> 延伸</div>
          <div class="legend-item"><span class="leg-edge applies"></span> 应用</div>
        </div>
      </div>
    </template>
    <el-empty v-else :image-size="120" description="请先选择一个课程查看知识图谱" />

    <!-- 知识点详情弹窗 -->
    <el-dialog v-model="detailVisible" title="知识点详情" width="500px">
      <template v-if="detailKp">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="名称">{{ detailKp.label }}</el-descriptions-item>
          <el-descriptions-item label="描述">{{ detailKp.description || '暂无描述' }}</el-descriptions-item>
          <el-descriptions-item label="重要度">
            <el-rate :model-value="detailKp.importance" disabled show-score text-color="#ff9900" />
          </el-descriptions-item>
          <el-descriptions-item label="难度">
            <el-rate :model-value="detailKp.difficulty" disabled show-score text-color="#ff9900" />
          </el-descriptions-item>
          <el-descriptions-item label="关键词">
            <el-tag v-for="kw in (detailKp.keywords || [])" :key="kw" size="small" style="margin-right:4px;">{{ kw }}</el-tag>
            <span v-if="!detailKp.keywords || detailKp.keywords.length === 0" style="color:#909399;">暂无</span>
          </el-descriptions-item>
          <el-descriptions-item label="层级">第 {{ detailKp.level }} 级</el-descriptions-item>
        </el-descriptions>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { ZoomIn, ZoomOut, Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { listCourses } from '../api/course'
import request from '../api/request'

const route = useRoute()
const kgContainer = ref(null)
const selectedCourseId = ref(null)
const courseList = ref([])
const building = ref(false)
let network = null
const nodes = ref([])
const edges = ref([])

// 详情弹窗
const detailVisible = ref(false)
const detailKp = ref(null)

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

async function rebuildGraph() {
  if (!selectedCourseId.value) return
  building.value = true
  try {
    const res = await request.post('/api/knowledge-graph/build/' + selectedCourseId.value)
    ElMessage.success(res.message || '知识图谱已重新生成')
    await loadGraph()
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '生成失败')
  } finally {
    building.value = false
  }
}

function getNodeColor(type) {
  if (type === 'course') return { bg: '#409eff', border: '#337ecc' }
  if (type === 'courseware') return { bg: '#67c23a', border: '#5daf34' }
  if (type === 'knowledge_point_l1') return { bg: '#1a3a5c', border: '#0f2440' }
  // knowledge_point_l2, knowledge_point_l3, or generic knowledge
  return { bg: '#5b9bd5', border: '#4a8ac4' }
}

function getNodeShape(type) {
  if (type === 'course') return 'star'
  if (type === 'courseware') return 'box'
  return 'dot'
}

function renderGraph() {
  if (!kgContainer.value) return

  const visNodes = new (window.vis.DataSet)(nodes.value.map(n => {
    const colors = getNodeColor(n.type)
    return {
      id: n.id,
      label: n.label,
      shape: getNodeShape(n.type),
      size: n.size || 20,
      color: {
        background: colors.bg,
        border: colors.border,
        highlight: { background: '#ff6b6b', border: '#ee5a24' }
      },
      font: { size: n.type === 'course' ? 16 : 13, color: '#1d2129' },
      // 存储额外数据供点击使用
      _kpData: n.type?.startsWith('knowledge_point') ? n : null,
    }
  }))

  const visEdges = new (window.vis.DataSet)(edges.value.map(e => {
    const style = getEdgeStyle(e.type)
    return {
      from: e.source,
      to: e.target,
      label: e.label,
      arrows: e.type === 'contains' || e.type === 'related' ? '' : 'to',
      color: { color: style.color, highlight: '#409eff' },
      font: { size: 10, color: '#909399', align: 'middle' },
      smooth: { type: 'curvedCW', roundness: 0.15 },
      dashes: style.dashes,
      width: e.weight ? 1 + e.weight * 2 : 1.5,
    }
  }))

  const data = { nodes: visNodes, edges: visEdges }
  const options = {
    layout: { improvedLayout: true, hierarchical: { enabled: false } },
    physics: {
      solver: 'barnesHut',
      barnesHut: { gravitationalConstant: -8000, springLength: 400, springConstant: 0.015 },
      stabilization: { iterations: 200 }
    },
    interaction: { hover: true, tooltipDelay: 200, zoomView: true, dragView: true },
    edges: { smooth: true },
    nodes: { borderWidth: 2, shadow: { enabled: true, size: 8 } },
  }

  network = new window.vis.Network(kgContainer.value, data, options)
  network.on('click', function(params) {
    if (params.nodes.length > 0) {
      const nodeId = params.nodes[0]
      const nodeData = visNodes.get(nodeId)
      // 点击知识点节点 → 显示详情
      if (nodeData?._kpData) {
        detailKp.value = nodeData._kpData
        detailVisible.value = true
      }
      // 高亮连接节点
      const connected = network.getConnectedNodes(nodeId)
      network.selectNodes([nodeId, ...connected], false)
    }
  })
}

function getEdgeStyle(type) {
  const styles = {
    prerequisite: { color: '#f56c6c', dashes: [8, 4] },
    contains:      { color: '#409eff', dashes: false },
    related:       { color: '#909399', dashes: [5, 5] },
    extends:       { color: '#67c23a', dashes: [3, 3] },
    applies:       { color: '#e6a23c', dashes: [6, 3] },
    source:        { color: '#c0c4cc', dashes: [2, 4] },
  }
  return styles[type] || { color: '#c0c4cc', dashes: false }
}

function zoomIn() { network && network.moveTo({ scale: network.getScale() * 1.2 }) }
function zoomOut() { network && network.moveTo({ scale: network.getScale() / 1.2 }) }
function fitView() { network && network.fit() }
</script>

<style scoped>
.kg-page { position: relative; padding: 0; }
.page-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
.page-title { font-size: 26px; font-weight: 600; color: #1d2129; margin: 0; }
.head-actions { display: flex; align-items: center; gap: 12px; }
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

/* 图例 */
.kg-legend {
  position: absolute;
  bottom: 16px;
  left: 16px;
  background: rgba(255,255,255,0.95);
  border-radius: 8px;
  padding: 12px 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  font-size: 13px;
  min-width: 180px;
}
.legend-title { font-weight: 600; font-size: 14px; margin-bottom: 8px; color: #303133; }
.legend-section { margin-bottom: 8px; }
.legend-label { color: #909399; font-size: 12px; margin-bottom: 4px; }
.legend-item { display: flex; align-items: center; gap: 6px; margin: 3px 0; color: #606266; }
.leg-node { width: 14px; height: 14px; border-radius: 50%; display: inline-block; flex-shrink: 0; }
.leg-edge { width: 24px; height: 2px; display: inline-block; flex-shrink: 0; }
.leg-edge.prereq { border-top: 2px dashed #f56c6c; }
.leg-edge.contains { background: #409eff; }
.leg-edge.related { border-top: 2px dashed #909399; }
.leg-edge.extends { background: #67c23a; height: 1px; }
.leg-edge.applies { background: #e6a23c; }
</style>
