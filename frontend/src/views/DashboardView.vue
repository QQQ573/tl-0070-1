<template>
  <div class="dashboard">
    <div class="stat-cards">
      <div class="stat-card">
        <div class="stat-label">藏品总数</div>
        <div class="stat-value">{{ overview.total_items }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">在库估值</div>
        <div class="stat-value">¥{{ overview.instock_value?.toFixed(2) }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">隐藏款数量</div>
        <div class="stat-value accent">{{ overview.hidden_count }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">置换中</div>
        <div class="stat-value warn">{{ overview.exchanging_count }}</div>
      </div>
    </div>

    <div class="chart-row">
      <div class="card chart-card">
        <h3>藏品状态分布</h3>
        <div ref="statusChartRef" class="chart-box"></div>
      </div>
      <div class="card chart-card">
        <h3>系列件数与购入额</h3>
        <div ref="seriesChartRef" class="chart-box"></div>
      </div>
    </div>

    <div class="card chart-card full">
      <h3>近六月成交置换次数</h3>
      <div ref="monthlyChartRef" class="chart-box wide"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, shallowRef } from 'vue'
import * as echarts from 'echarts'
import { statsApi } from '../api'

const overview = ref({
  total_items: 0,
  instock_count: 0,
  out_count: 0,
  exchanging_count: 0,
  hidden_count: 0,
  instock_value: 0,
  series_stats: [],
})
const monthly = ref([])

const statusChartRef = ref(null)
const seriesChartRef = ref(null)
const monthlyChartRef = ref(null)
const charts = shallowRef([])

function initStatusChart() {
  const chart = echarts.init(statusChartRef.value)
  chart.setOption({
    tooltip: { trigger: 'item' },
    color: ['#6b9e78', '#c4a882', '#d4846a'],
    series: [{
      type: 'pie',
      radius: ['42%', '68%'],
      label: { formatter: '{b}\n{c}件' },
      data: [
        { name: '在库', value: overview.value.instock_count },
        { name: '已出', value: overview.value.out_count },
        { name: '置换中', value: overview.value.exchanging_count },
      ],
    }],
  })
  charts.value.push(chart)
}

function initSeriesChart() {
  const stats = overview.value.series_stats.slice(0, 8)
  const chart = echarts.init(seriesChartRef.value)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['件数', '购入额'] },
    grid: { left: 48, right: 48, bottom: 32 },
    xAxis: { type: 'category', data: stats.map(s => s.series), axisLabel: { rotate: 20 } },
    yAxis: [
      { type: 'value', name: '件' },
      { type: 'value', name: '元', splitLine: { show: false } },
    ],
    series: [
      { name: '件数', type: 'bar', data: stats.map(s => s.count), itemStyle: { color: '#8b6f5c' } },
      { name: '购入额', type: 'line', yAxisIndex: 1, data: stats.map(s => s.total_value), itemStyle: { color: '#d4846a' } },
    ],
  })
  charts.value.push(chart)
}

function initMonthlyChart() {
  const chart = echarts.init(monthlyChartRef.value)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 48, right: 24, bottom: 32 },
    xAxis: { type: 'category', data: monthly.value.map(m => m.month) },
    yAxis: { type: 'value', minInterval: 1 },
    series: [{
      type: 'line',
      smooth: true,
      areaStyle: { color: 'rgba(139,111,92,0.2)' },
      itemStyle: { color: '#6b4c3b' },
      data: monthly.value.map(m => m.count),
    }],
  })
  charts.value.push(chart)
}

function handleResize() {
  charts.value.forEach(c => c.resize())
}

async function loadDashboard() {
  const { data } = await statsApi.dashboard()
  overview.value = data.overview
  monthly.value = data.monthly_exchanges
  initStatusChart()
  initSeriesChart()
  initMonthlyChart()
}

onMounted(async () => {
  await loadDashboard()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  charts.value.forEach(c => c.dispose())
})
</script>

<style scoped>
.dashboard { display: flex; flex-direction: column; gap: 20px; }
.stat-cards { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.stat-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.stat-label { font-size: 13px; color: #888; margin-bottom: 8px; }
.stat-value { font-size: 28px; font-weight: 700; color: #2c2420; }
.stat-value.accent { color: #9b59b6; }
.stat-value.warn { color: #d4846a; }
.chart-row { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.chart-card h3 { font-size: 15px; margin-bottom: 12px; color: #4a3f38; }
.chart-box { height: 280px; }
.chart-box.wide { height: 260px; }
.chart-card.full { margin-top: 0; }
@media (max-width: 900px) {
  .stat-cards { grid-template-columns: repeat(2, 1fr); }
  .chart-row { grid-template-columns: 1fr; }
}
</style>
