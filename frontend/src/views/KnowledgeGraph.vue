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
      <div v-if="!graphData.nodes.length" class="empty-state">
        <el-icon :size="64" color="#c0c4cc"><Connection /></el-icon>
        <p>搜索实体以查看知识图谱</p>
      </div>
      <div v-else class="graph-container" ref="graphRef"></div>
      <!-- 搜索结果列表 -->
      <div v-if="searchResults.length" class="results-panel">
        <h4>搜索结果</h4>
        <div v-for="r in searchResults" :key="r.name" class="result-item" @click="loadSubgraph(r.name)">
          <el-tag size="small">{{ r.labels?.[0] || 'Entity' }}</el-tag>
          <span>{{ r.name }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import * as echarts from 'echarts'
import { Connection } from '@element-plus/icons-vue'
import axios from 'axios'

const searchQuery = ref('')
const searchResults = ref([])
const graphData = ref({ nodes: [], edges: [] })
const graphRef = ref()
const loading = ref(false)

async function handleSearch() {
  if (!searchQuery.value.trim()) return
  loading.value = true
  try {
    const headers = { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    const { data } = await axios.get('/api/knowledge/search', { params: { q: searchQuery.value }, headers })
    searchResults.value = data.results || []
    if (searchResults.value.length > 0) {
      await loadSubgraph(searchResults.value[0].name)
    }
  } finally {
    loading.value = false
  }
}

async function loadSubgraph(center) {
  const headers = { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
  const { data } = await axios.get('/api/knowledge/graph', { params: { center, depth: 2 }, headers })
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
    symbolSize: 40,
    category: (n.labels || ['default'])[0],
    label: { show: true },
  }))

  const edges = graphData.value.edges.map(e => ({
    source: e.source,
    target: e.target,
    label: { show: true, formatter: e.type },
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
      label: { position: 'right' },
      force: { repulsion: 200 },
      lineStyle: { color: 'source', curveness: 0.3 },
    }],
  })
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
  padding: 24px;
  display: flex;
  gap: 16px;
  height: calc(100vh - 64px);
}
.graph-container {
  flex: 1;
  background: #fff;
  border-radius: 8px;
}
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #909399;
}
.results-panel {
  width: 280px;
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  overflow-y: auto;
}
.results-panel h4 {
  margin-bottom: 12px;
  color: #303133;
}
.result-item {
  padding: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  border-radius: 4px;
}
.result-item:hover {
  background: #f5f7fa;
}
</style>
