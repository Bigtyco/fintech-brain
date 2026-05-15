<template>
  <div class="kg-layout">
    <div class="top-nav">
      <el-button @click="$router.push('/chat')" text>返回对话</el-button>
      <h3>知识图谱</h3>
      <div class="search-box">
        <el-input v-model="searchQuery" placeholder="搜索实体..." @keydown.enter="handleSearch" clearable>
          <template #append>
            <el-button @click="handleSearch" :loading="loading">搜索</el-button>
          </template>
        </el-input>
      </div>
    </div>
    <div class="kg-content">
      <!-- 左侧：实体与关系列表 -->
      <div class="left-panel">
        <div class="panel-section">
          <h4>实体 ({{ allEntities.length }})</h4>
          <div class="entity-list">
            <div
              v-for="entity in allEntities"
              :key="entity.name"
              class="entity-item"
              :class="{ active: selectedEntity === entity.name }"
              @click="selectEntity(entity.name)"
            >
              <el-tag size="small" :type="tagType(entity.labels?.[0])">{{ entity.labels?.[0] || 'Entity' }}</el-tag>
              <span class="entity-name">{{ entity.name }}</span>
            </div>
          </div>
        </div>
        <div class="panel-section">
          <h4>关系 ({{ allRelations.length }})</h4>
          <div class="relation-list">
            <div
              v-for="(rel, idx) in allRelations"
              :key="idx"
              class="relation-item"
            >
              <span class="rel-source">{{ rel.source }}</span>
              <el-tag size="small" type="warning">{{ rel.relation }}</el-tag>
              <span class="rel-target">{{ rel.target }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：图谱 -->
      <div class="right-panel">
        <div v-if="!graphData.nodes.length" class="empty-state">
          <el-icon :size="64" color="#c0c4cc"><Connection /></el-icon>
          <p>点击左侧实体查看知识图谱</p>
        </div>
        <div v-else class="graph-container" ref="graphRef"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import * as echarts from 'echarts'
import { Connection } from '@element-plus/icons-vue'
import axios from 'axios'

const searchQuery = ref('')
const allEntities = ref([])
const allRelations = ref([])
const graphData = ref({ nodes: [], edges: [] })
const graphRef = ref()
const loading = ref(false)
const selectedEntity = ref('')

onMounted(async () => {
  try {
    const { data } = await axios.get('/api/knowledge/all', { withCredentials: true })
    allEntities.value = data.entities || []
    allRelations.value = data.relations || []
  } catch (e) {
    console.error('Failed to load knowledge graph data:', e)
  }
})

function tagType(label) {
  const map = { Company: '', Industry: 'success', Person: 'danger', RiskEvent: 'warning', Policy: 'info' }
  return map[label] || ''
}

async function selectEntity(name) {
  selectedEntity.value = name
  await loadSubgraph(name)
}

async function handleSearch() {
  if (!searchQuery.value.trim()) return
  loading.value = true
  try {
    const { data } = await axios.get('/api/knowledge/search', { params: { q: searchQuery.value }, withCredentials: true })
    const results = data.results || []
    if (results.length > 0) {
      selectedEntity.value = results[0].name
      await loadSubgraph(results[0].name)
    }
  } finally {
    loading.value = false
  }
}

async function loadSubgraph(center) {
  const { data } = await axios.get('/api/knowledge/graph', { params: { center, depth: 2 }, withCredentials: true })
  graphData.value = { nodes: data.nodes || [], edges: data.edges || [] }
  await nextTick()
  renderGraph()
}

function renderGraph() {
  if (!graphRef.value) return
  const chart = echarts.init(graphRef.value)

  const nodes = graphData.value.nodes.map(n => ({
    id: n.id,
    name: n.name,
    symbolSize: 50,
    category: (n.labels || ['default'])[0],
    label: { show: true, position: 'inside', fontSize: 12, color: '#fff' },
  }))

  const edges = graphData.value.edges.map(e => ({
    source: e.source,
    target: e.target,
    label: { show: true, formatter: e.type, fontSize: 10 },
  }))

  const categories = [...new Set(nodes.map(n => n.category))].map(c => ({ name: c }))

  chart.setOption({
    tooltip: {},
    legend: { data: categories.map(c => c.name) },
    series: [{
      type: 'graph',
      layout: 'force',
      data: nodes,
      links: edges,
      categories,
      roam: true,
      label: { position: 'inside', fontSize: 12, color: '#fff' },
      force: { repulsion: 300, gravity: 0.1 },
      lineStyle: { color: 'source', curveness: 0.3 },
      emphasis: { focus: 'adjacency', label: { fontSize: 14, fontWeight: 'bold' } },
    }],
  })

  chart.resize()
  window.addEventListener('resize', () => chart.resize())
}
</script>

<style scoped>
.kg-layout {
  min-height: 100vh;
  background: #f0f2f5;
}
.top-nav {
  background: #fff;
  padding: 12px 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.top-nav h3 {
  font-size: 18px;
  color: #1a1a2e;
  white-space: nowrap;
}
.search-box {
  flex: 1;
  max-width: 400px;
}
.kg-content {
  padding: 16px;
  display: flex;
  gap: 16px;
  height: calc(100vh - 64px);
}
.left-panel {
  width: 300px;
  background: #fff;
  border-radius: 8px;
  overflow-y: auto;
  flex-shrink: 0;
}
.panel-section {
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
}
.panel-section h4 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 14px;
}
.entity-list, .relation-list {
  max-height: 40vh;
  overflow-y: auto;
}
.entity-item {
  padding: 6px 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  border-radius: 4px;
  font-size: 13px;
}
.entity-item:hover, .entity-item.active {
  background: #ecf5ff;
}
.entity-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.relation-item {
  padding: 4px 8px;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #606266;
}
.rel-source, .rel-target {
  max-width: 80px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.right-panel {
  flex: 1;
  background: #fff;
  border-radius: 8px;
  position: relative;
}
.graph-container {
  width: 100%;
  height: 100%;
}
.empty-state {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #909399;
}
</style>
