<template>
  <div class="dashboard-layout">
    <div class="top-nav">
      <el-button @click="$router.push('/chat')" text>返回对话</el-button>
      <h3>风控看板</h3>
      <div></div>
    </div>
    <div class="dashboard-content">
      <!-- 概览卡片 -->
      <div class="overview-cards">
        <el-card v-for="card in overviewCards" :key="card.title" shadow="hover">
          <div class="card-inner">
            <div>
              <p class="card-value">{{ card.value }}</p>
              <p class="card-title">{{ card.title }}</p>
            </div>
            <el-icon :size="40" :color="card.color"><component :is="card.icon" /></el-icon>
          </div>
        </el-card>
      </div>

      <!-- 图表区 -->
      <div class="charts-row">
        <el-card shadow="hover">
          <template #header>风险趋势</template>
          <v-chart :option="trendOption" style="height: 350px" autoresize />
        </el-card>
        <el-card shadow="hover">
          <template #header>风险分布</template>
          <v-chart :option="pieOption" style="height: 350px" autoresize />
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, PieChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent, TitleComponent } from 'echarts/components'
import { Warning, Document, Connection, DataAnalysis } from '@element-plus/icons-vue'
import axios from 'axios'

use([CanvasRenderer, LineChart, PieChart, GridComponent, TooltipComponent, LegendComponent, TitleComponent])

const overview = ref({})
const trendData = ref({})
const distData = ref({})

const overviewCards = computed(() => [
  { title: '已索引文档', value: overview.value.documents_indexed || 0, icon: 'Document', color: '#409eff' },
  { title: '对话总数', value: overview.value.conversations || 0, icon: 'DataAnalysis', color: '#67c23a' },
  { title: 'AI 回复数', value: overview.value.ai_responses || 0, icon: 'Connection', color: '#e6a23c' },
  { title: '风控查询', value: overview.value.risk_queries || 0, icon: 'Warning', color: '#f56c6c' },
])

const trendOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  legend: { data: ['风控查询', '投研查询'] },
  xAxis: { type: 'category', data: trendData.value.labels || [] },
  yAxis: { type: 'value' },
  series: [
    { name: '风控查询', type: 'line', data: trendData.value.risk_queries || [], smooth: true },
    { name: '投研查询', type: 'line', data: trendData.value.research_queries || [], smooth: true },
  ],
}))

const pieOption = computed(() => ({
  tooltip: { trigger: 'item' },
  series: [{
    type: 'pie',
    radius: '60%',
    data: (distData.value.categories || []).map((c, i) => ({
      name: c,
      value: (distData.value.values || [])[i] || 0,
    })),
  }],
}))

onMounted(async () => {
  const cfg = { withCredentials: true }
  const [o, t, d] = await Promise.all([
    axios.get('/api/dashboard/overview', cfg),
    axios.get('/api/dashboard/risk-trends', cfg),
    axios.get('/api/dashboard/risk-distribution', cfg),
  ])
  overview.value = o.data
  trendData.value = t.data
  distData.value = d.data
})
</script>

<style scoped>
.dashboard-layout {
  min-height: 100vh;
  background: #f0f2f5;
}
.top-nav {
  background: #fff;
  padding: 12px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.top-nav h3 {
  font-size: 18px;
  color: #1a1a2e;
}
.dashboard-content {
  padding: 24px;
}
.overview-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}
.card-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.card-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}
.card-title {
  color: #909399;
  margin-top: 4px;
}
.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
</style>
