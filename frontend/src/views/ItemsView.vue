<template>
  <div>
    <div class="card">
      <div class="filter-bar">
        <div class="filter-item">
          <label>关键词</label>
          <input v-model="filters.keyword" placeholder="名称/款式ID/系列" @keyup.enter="loadItems(1)" />
        </div>
        <div class="filter-item">
          <label>系列</label>
          <select v-model="filters.series" @change="loadItems(1)">
            <option value="">全部系列</option>
            <option v-for="s in seriesList" :key="s" :value="s">{{ s }}</option>
          </select>
        </div>
        <div class="filter-item">
          <label>稀有度</label>
          <select v-model="filters.rarity" @change="loadItems(1)">
            <option value="">全部</option>
            <option value="常规">常规</option>
            <option value="隐藏">隐藏</option>
            <option value="限定">限定</option>
          </select>
        </div>
        <div class="filter-item">
          <label>&nbsp;</label>
          <button class="btn btn-primary" @click="loadItems(1)">检索</button>
        </div>
        <div class="filter-item" style="margin-left:auto">
          <label>&nbsp;</label>
          <button class="btn btn-primary" @click="openForm()">+ 新增藏品</button>
        </div>
      </div>
    </div>

    <div class="card">
      <div v-if="items.length === 0" class="empty-state">
        <p>暂无藏品记录</p>
        <p style="font-size:13px">点击「新增藏品」开始添加</p>
      </div>
      <table v-else>
        <thead>
          <tr>
            <th>图片</th>
            <th>系列</th>
            <th>名称</th>
            <th>款式ID</th>
            <th>稀有度</th>
            <th>获取方式</th>
            <th>购入价</th>
            <th>状态</th>
            <th>批次号</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="item in items"
            :key="item.id"
            :class="{ 'row-active': selectedItem?.id === item.id }"
            @click="openDetail(item)"
            style="cursor:pointer"
          >
            <td>
              <img v-if="item.image_path" :src="item.image_path" style="width:48px;height:48px;object-fit:cover;border-radius:8px;" />
              <span v-else style="color:#ccc;font-size:24px;">🧸</span>
            </td>
            <td>{{ item.series }}</td>
            <td><strong>{{ item.name }}</strong></td>
            <td>{{ item.style_id }}</td>
            <td><span class="tag" :class="rarityClass(item.rarity)">{{ item.rarity }}</span></td>
            <td>{{ item.acquisition_method }}</td>
            <td>¥{{ item.purchase_price?.toFixed(2) }}</td>
            <td><span class="tag" :class="statusClass(item.status)">{{ item.status }}</span></td>
            <td>{{ item.batch_no || '-' }}</td>
            <td>
              <div class="actions-cell" @click.stop>
                <button class="btn btn-secondary btn-sm" @click="openForm(item)">编辑</button>
                <button class="btn btn-danger btn-sm" @click="handleDelete(item.id)">删除</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <div class="pagination" v-if="total > 0">
        <button :disabled="page <= 1" @click="loadItems(page - 1)">上一页</button>
        <span class="page-info">第 {{ page }} / {{ totalPages }} 页 · 共 {{ total }} 条</span>
        <button :disabled="page >= totalPages" @click="loadItems(page + 1)">下一页</button>
      </div>
    </div>

    <div v-if="selectedItem" class="detail-drawer">
      <div class="drawer-header">
        <h3>{{ selectedItem.name }} · 行情对照</h3>
        <button class="btn btn-secondary btn-sm" @click="closeDetail">关闭</button>
      </div>
      <div class="drawer-body">
        <div class="drawer-meta">
          <span>款式 ID：<strong>{{ selectedItem.style_id }}</strong></span>
          <span>购入价：<strong>¥{{ selectedItem.purchase_price?.toFixed(2) }}</strong></span>
        </div>
        <div v-if="trend.latest_price != null" class="diff-box" :class="diffClass">
          最近成交 ¥{{ trend.latest_price?.toFixed(2) }}
          <span v-if="trend.diff_percent != null">
            （较购入 {{ trend.diff_percent >= 0 ? '+' : '' }}{{ trend.diff_percent }}%）
          </span>
        </div>
        <div v-else class="diff-box neutral">暂无行情数据，请先在「行情参考」页录入</div>
        <div ref="trendChartRef" class="trend-chart"></div>
        <router-link to="/market" class="link-market">去录入行情 →</router-link>
      </div>
    </div>

    <div v-if="showForm" class="modal-overlay" @click.self="showForm = false">
      <div class="modal">
        <div class="modal-title">{{ editingItem ? '编辑藏品' : '新增藏品' }}</div>
        <div class="form-row">
          <div class="form-group">
            <label>系列 *</label>
            <input v-model="form.series" placeholder="如：The Monsters" />
          </div>
          <div class="form-group">
            <label>名称 *</label>
            <input v-model="form.name" placeholder="如：Labubu 隐藏款" />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>款式ID *</label>
            <input v-model="form.style_id" placeholder="如：TM-001" />
          </div>
          <div class="form-group">
            <label>稀有度 *</label>
            <select v-model="form.rarity" @change="onRarityChange">
              <option value="常规">常规</option>
              <option value="隐藏">隐藏</option>
              <option value="限定">限定</option>
            </select>
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>获取方式 *</label>
            <select v-model="form.acquisition_method">
              <option value="盲盒">盲盒</option>
              <option value="直购">直购</option>
              <option value="置换">置换</option>
            </select>
          </div>
          <div class="form-group">
            <label>购入价</label>
            <input v-model.number="form.purchase_price" type="number" step="0.01" placeholder="0.00" />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>状态 *</label>
            <select v-model="form.status">
              <option value="在库">在库</option>
              <option value="已出">已出</option>
              <option value="置换中">置换中</option>
            </select>
          </div>
          <div class="form-group">
            <label>获取批次号 <span v-if="form.rarity === '隐藏'" style="color:#e74c3c">*</span></label>
            <input v-model="form.batch_no" :placeholder="form.rarity === '隐藏' ? '如: AB202601-01' : '选填'" />
          </div>
        </div>
        <div class="form-group">
          <label>图片</label>
          <input type="file" accept="image/*" @change="handleImageUpload" />
          <div v-if="form.image_path" style="margin-top:8px;">
            <img :src="form.image_path" style="max-width:120px;max-height:120px;border-radius:8px;" />
          </div>
        </div>
        <div class="form-group">
          <label>备注</label>
          <textarea v-model="form.notes" rows="2" placeholder="其他备注"></textarea>
        </div>
        <div v-if="formError" style="color:#e74c3c;font-size:13px;margin-bottom:12px;">{{ formError }}</div>
        <div class="modal-actions">
          <button class="btn btn-secondary" @click="showForm = false">取消</button>
          <button class="btn btn-primary" @click="handleSubmit">{{ editingItem ? '保存' : '创建' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { itemsApi, uploadsApi, marketApi } from '../api'

const items = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 10
const seriesList = ref([])

const filters = ref({ keyword: '', series: '', rarity: '' })

const showForm = ref(false)
const editingItem = ref(null)
const form = ref(getEmptyForm())
const formError = ref('')

const selectedItem = ref(null)
const trend = ref({ records: [], latest_price: null, diff_percent: null })
const trendChartRef = ref(null)
let trendChart = null

function getEmptyForm() {
  return {
    series: '',
    style_id: '',
    name: '',
    rarity: '常规',
    acquisition_method: '盲盒',
    purchase_price: 0,
    status: '在库',
    batch_no: '',
    image_path: '',
    notes: '',
  }
}

const totalPages = computed(() => Math.ceil(total.value / pageSize))

const diffClass = computed(() => {
  if (trend.value.diff_percent == null) return 'neutral'
  return trend.value.diff_percent >= 0 ? 'up' : 'down'
})

function renderTrendChart() {
  if (!trendChartRef.value) return
  if (trendChart) trendChart.dispose()
  trendChart = echarts.init(trendChartRef.value)
  const records = trend.value.records || []
  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 40, right: 16, top: 24, bottom: 28 },
    xAxis: { type: 'category', data: records.map(r => r.record_date) },
    yAxis: { type: 'value', scale: true },
    series: [{
      type: 'line',
      smooth: true,
      data: records.map(r => r.deal_price),
      itemStyle: { color: '#6b4c3b' },
      markLine: selectedItem.value ? {
        silent: true,
        data: [{ yAxis: selectedItem.value.purchase_price, name: '购入价' }],
        lineStyle: { color: '#27ae60', type: 'dashed' },
      } : undefined,
    }],
  })
}

async function openDetail(item) {
  selectedItem.value = item
  try {
    const { data } = await marketApi.trend(item.style_id, {
      purchase_price: item.purchase_price,
      limit: 10,
    })
    trend.value = data
    await nextTick()
    renderTrendChart()
  } catch (e) {
    console.error(e)
  }
}

function closeDetail() {
  selectedItem.value = null
  if (trendChart) {
    trendChart.dispose()
    trendChart = null
  }
}

function rarityClass(rarity) {
  if (rarity === '隐藏') return 'tag-hidden'
  if (rarity === '限定') return 'tag-limited'
  return 'tag-normal'
}

function statusClass(status) {
  if (status === '在库') return 'tag-instock'
  if (status === '已出') return 'tag-out'
  return 'tag-exchanging'
}

function onRarityChange() {
  if (form.value.rarity !== '隐藏') {
    form.value.batch_no = ''
  }
}

async function loadItems(p = 1) {
  page.value = p
  const params = { page: p, page_size: pageSize }
  if (filters.value.keyword) params.keyword = filters.value.keyword
  if (filters.value.series) params.series = filters.value.series
  if (filters.value.rarity) params.rarity = filters.value.rarity
  try {
    const { data } = await itemsApi.list(params)
    items.value = data.items
    total.value = data.total
  } catch (e) {
    console.error(e)
  }
}

async function loadSeries() {
  try {
    const { data } = await itemsApi.series()
    seriesList.value = data
  } catch (e) {
    console.error(e)
  }
}

function openForm(item = null) {
  editingItem.value = item
  formError.value = ''
  if (item) {
    form.value = { ...item }
  } else {
    form.value = getEmptyForm()
  }
  showForm.value = true
}

async function handleImageUpload(e) {
  const file = e.target.files[0]
  if (!file) return
  try {
    const { data } = await uploadsApi.upload(file)
    form.value.image_path = data.path
  } catch (err) {
    alert('图片上传失败：' + (err.response?.data?.detail || err.message))
  }
}

async function handleSubmit() {
  formError.value = ''
  const payload = { ...form.value }
  if (!payload.series || !payload.name || !payload.style_id) {
    formError.value = '系列、名称、款式ID 为必填项'
    return
  }
  try {
    if (editingItem.value) {
      await itemsApi.update(editingItem.value.id, payload)
    } else {
      await itemsApi.create(payload)
    }
    showForm.value = false
    await loadItems(page.value)
    await loadSeries()
  } catch (err) {
    const detail = err.response?.data?.detail
    if (typeof detail === 'object') {
      formError.value = detail.map(e => e.msg).join('; ')
    } else {
      formError.value = detail || '操作失败'
    }
  }
}

async function handleDelete(id) {
  if (!confirm('确定删除该藏品？（软删除，可恢复）')) return
  try {
    await itemsApi.remove(id)
    await loadItems(page.value)
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => {
  loadItems(1)
  loadSeries()
})

onUnmounted(() => {
  if (trendChart) trendChart.dispose()
})
</script>

<style scoped>
.row-active { background: #faf6f2 !important; }
.detail-drawer {
  position: fixed;
  top: 60px;
  right: 0;
  width: 380px;
  height: calc(100vh - 60px);
  background: #fff;
  box-shadow: -4px 0 20px rgba(0,0,0,0.1);
  z-index: 90;
  display: flex;
  flex-direction: column;
}
.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #eee;
}
.drawer-header h3 { font-size: 15px; }
.drawer-body { padding: 20px; flex: 1; overflow-y: auto; }
.drawer-meta { display: flex; flex-direction: column; gap: 8px; font-size: 14px; margin-bottom: 16px; }
.diff-box { padding: 12px; border-radius: 8px; font-size: 14px; margin-bottom: 16px; }
.diff-box.up { background: #fdecea; color: #c0392b; }
.diff-box.down { background: #e8f8ef; color: #27ae60; }
.diff-box.neutral { background: #f5f5f5; color: #888; }
.trend-chart { height: 220px; margin-bottom: 12px; }
.link-market { font-size: 13px; color: #6b4c3b; text-decoration: none; }
.link-market:hover { text-decoration: underline; }
</style>
