<template>
  <div class="kg-page">
    <div class="page-head">
      <div class="page-head-left">
        <h2 class="page-title">知识图谱</h2>
        <p class="page-subtitle">可视化课程知识点结构</p>
      </div>
      <div class="head-actions">
        <el-select v-model="selectedCourseId" placeholder="请选择课程" @change="loadGraph" style="width: 220px" clearable>
          <el-option v-for="c in courseList" :key="c.id" :label="c.course_name" :value="c.id" />
        </el-select>
        <el-button type="primary" :icon="Refresh" @click="rebuildGraph" :loading="building" :disabled="!selectedCourseId" round>重新生成图谱</el-button>
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
    <div v-else class="empty-state">
      <div class="empty-graphic"><div class="empty-orb"></div><el-icon :size="48" color="#5b8def" class="empty-icon"><Share /></el-icon></div>
      <p class="empty-title">请先选择一个课程</p>
      <p class="empty-desc">选择课程后即可查看知识图谱</p>
    </div>
    <el-dialog v-model="detailVisible" title="知识点详情" width="500px">
      <template v-if="detailKp">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="名称">{{ detailKp.label }}</el-descriptions-item>
          <el-descriptions-item label="描述">{{ detailKp.description || '暂无描述' }}</el-descriptions-item>
          <el-descriptions-item label="重要度"><el-rate :model-value="detailKp.importance" disabled show-score text-color="#ff9900" /></el-descriptions-item>
          <el-descriptions-item label="难度"><el-rate :model-value="detailKp.difficulty" disabled show-score text-color="#ff9900" /></el-descriptions-item>
          <el-descriptions-item label="关键词">
            <el-tag v-for="kw in (detailKp.keywords || [])" :key="kw" size="small" style="margin-right:4px;">{{ kw }}</el-tag>
            <span v-if="!detailKp.keywords || detailKp.keywords.length === 0" style="color:#909399;">暂无</span>
          </el-descriptions-item>
          <el-descriptions-item label="层级">第{{ detailKp.level }} 级</el-descriptions-item>
        </el-descriptions>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { ZoomIn, ZoomOut, Refresh, Share } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { listCourses } from '../api/course'
import request from '../api/request'
const route = useRoute(); const kgContainer = ref(null); const selectedCourseId = ref(null); const courseList = ref([]); const building = ref(false)
let network = null; const nodes = ref([]); const edges = ref([]); const detailVisible = ref(false); const detailKp = ref(null)
onMounted(async () => { try { const res = await listCourses(); courseList.value = res.data?.courses || [] } catch { courseList.value = [] }; const urlCourseId = route.params.courseId; if (urlCourseId) { selectedCourseId.value = Number(urlCourseId); await nextTick(); await loadGraph() } })
async function loadGraph() { if (!selectedCourseId.value) return; try { const res = await request.get('/api/knowledge-graph/' + selectedCourseId.value); const data = res.data; nodes.value = data?.nodes || []; edges.value = data?.edges || []; await nextTick(); renderGraph() } catch {} }
async function rebuildGraph() { if (!selectedCourseId.value) return; building.value = true; try { const res = await request.post('/api/knowledge-graph/build/' + selectedCourseId.value); ElMessage.success(res.message || '知识图谱已重新生成'); await loadGraph() } catch (e) { ElMessage.error(e.response?.data?.message || '生成失败') } finally { building.value = false } }
function getNodeColor(type) { if (type === 'course') return { bg: '#409eff', border: '#337ecc' }; if (type === 'courseware') return { bg: '#67c23a', border: '#5daf34' }; if (type === 'knowledge_point_l1') return { bg: '#1a3a5c', border: '#0f2440' }; return { bg: '#5b9bd5', border: '#4a8ac4' } }
function getNodeShape(type) { if (type === 'course') return 'star'; if (type === 'courseware') return 'box'; return 'dot' }
function getEdgeStyle(type) { const s = { prerequisite: { color: '#f56c6c', dashes: [8, 4] }, contains: { color: '#409eff', dashes: false }, related: { color: '#909399', dashes: [5, 5] }, extends: { color: '#67c23a', dashes: [3, 3] }, applies: { color: '#e6a23c', dashes: [6, 3] }, source: { color: '#c0c4cc', dashes: [2, 4] } }; return s[type] || { color: '#c0c4cc', dashes: false } }
function renderGraph() {
  if (!kgContainer.value) return;
  const visNodes = new (window.vis.DataSet)(nodes.value.map(n => { const c = getNodeColor(n.type); return { id: n.id, label: n.label, shape: getNodeShape(n.type), size: n.size || 20, color: { background: c.bg, border: c.border, highlight: { background: '#ff6b6b', border: '#ee5a24' } }, font: { size: n.type === 'course' ? 17 : 14, color: '#1d2129', face: '-apple-system, BlinkMacSystemFont, sans-serif' }, _kpData: n.type?.startsWith('knowledge_point') ? n : null } }))
  const visEdges = new (window.vis.DataSet)(edges.value.map(e => { const s = getEdgeStyle(e.type); return { from: e.source, to: e.target, label: e.label, arrows: e.type === 'contains' || e.type === 'related' ? '' : 'to', color: { color: s.color, highlight: '#409eff' }, font: { size: 11, color: '#909399', align: 'middle', face: '-apple-system, sans-serif' }, smooth: { type: 'curvedCW', roundness: 0.15 }, dashes: s.dashes, width: e.weight ? 1 + e.weight * 2 : 1.5 } }))
  const data = { nodes: visNodes, edges: visEdges }
  const options = { layout: { improvedLayout: true, hierarchical: { enabled: false } }, physics: { solver: 'barnesHut', barnesHut: { gravitationalConstant: -8000, springLength: 400, springConstant: 0.015 }, stabilization: { iterations: 200 } }, interaction: { hover: true, tooltipDelay: 200, zoomView: true, dragView: true }, edges: { smooth: true }, nodes: { borderWidth: 2, shadow: { enabled: true, size: 8 } } }
  network = new window.vis.Network(kgContainer.value, data, options)
  network.on('click', function(params) { if (params.nodes.length > 0) { const nodeData = visNodes.get(params.nodes[0]); if (nodeData?._kpData) { detailKp.value = nodeData._kpData; detailVisible.value = true }; const connected = network.getConnectedNodes(params.nodes[0]); network.selectNodes([params.nodes[0], ...connected], false) } })
}
function zoomIn() { network && network.moveTo({ scale: network.getScale() * 1.2 }) }
function zoomOut() { network && network.moveTo({ scale: network.getScale() / 1.2 }) }
function fitView() { network && network.fit() }
</script>

<style scoped>
.kg-page { position: relative; padding: 0; }
.page-head { display: flex; align-items: flex-end; justify-content: space-between; position: relative; margin-bottom: 24px; }
.page-head-left {}
.page-title { font-size: 26px; font-weight: 700; color: var(--text-primary); margin: 0; letter-spacing: -0.5px; }
.page-title::after { content: ""; display: block; width: 40px; height: 3px; background: linear-gradient(90deg, #7c5ce7,#4a7cff); border-radius: 2px; margin-top: 8px; opacity: 0.5; } 
.page-subtitle { font-size: 14px; color: var(--text-tertiary); margin-top: 4px; }
.head-actions { display: flex; align-items: center; gap: 12px; }
.kg-toolbar { display: flex; align-items: center; gap: 8px; padding: 14px 20px; background: rgba(244,247,253,0.92); backdrop-filter: blur(14px); border-radius: 14px; margin-bottom: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border: 1px solid rgba(255,255,255,0.3); }
.kg-info { font-size: 14px; color: var(--text-tertiary); margin-left: 12px; }
.kg-container { width: 100%; height: calc(100vh - 280px); background: linear-gradient(135deg, #f8faff 0%, #f0f4ff 50%, #f5f0ff 100%); border-radius: 14px; border: 1px solid var(--border-color); overflow: hidden; box-shadow: var(--shadow-sm); }
.kg-legend { position: absolute; bottom: 16px; left: 16px; background: rgba(255,255,255,0.92); backdrop-filter: blur(12px); border-radius: 12px; padding: 14px 18px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); font-size: 13px; min-width: 180px; border: 1px solid rgba(255,255,255,0.3); }
.legend-title { font-weight: 600; font-size: 14px; margin-bottom: 10px; color: var(--text-primary); }
.legend-section { margin-bottom: 8px; }
.legend-label { color: var(--text-tertiary); font-size: 12px; margin-bottom: 4px; }
.legend-item { display: flex; align-items: center; gap: 6px; margin: 3px 0; color: var(--text-secondary); }
.leg-node { width: 14px; height: 14px; border-radius: 50%; display: inline-block; flex-shrink: 0; }
.leg-edge { width: 24px; height: 2px; display: inline-block; flex-shrink: 0; }
.leg-edge.prereq { border-top: 2px dashed #f56c6c; }
.leg-edge.contains { background: #409eff; }
.leg-edge.related { border-top: 2px dashed #909399; }
.leg-edge.extends { background: #67c23a; height: 1px; }
.leg-edge.applies { background: #e6a23c; }

.empty-state { text-align: center; padding: 80px 20px; }
.empty-graphic { position: relative; width: 100px; height: 100px; margin: 0 auto 24px; display: flex; align-items: center; justify-content: center; }
.empty-orb { position: absolute; width: 100%; height: 100%; border-radius: 50%; background: radial-gradient(circle at 30% 30%, #e8f4fd, #d0e8ff); opacity: 0.4; animation: orb-pulse 4s ease-in-out infinite; }
@keyframes orb-pulse { 0%,100% { transform: scale(1); opacity: 0.4; } 50% { transform: scale(1.1); opacity: 0.6; } }
.empty-icon { position: relative; z-index: 1; }
.empty-title { font-size: 20px; font-weight: 600; color: var(--text-primary); margin: 0 0 8px; }
.empty-desc { font-size: 15px; color: var(--text-tertiary); margin: 0; }
</style>

