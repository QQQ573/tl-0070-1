<template>
  <div>
    <div class="card">
      <div class="filter-bar">
        <div class="filter-item">
          <label>款式 ID</label>
          <input v-model="filters.style_id" placeholder="如 TM-001" @keyup.enter="loadPrices(1)" />
        </div>
        <div class="filter-item">
          <label>起始日期</label>
          <input v-model="filters.date_from" type="date" />
        </div>
        <div class="filter-item">
          <label>截止日期</label>
          <input v-model="filters.date_to" type="date" />
        </div>
        <div class="filter-item">
          <label>&nbsp;</label>
          <button class="btn btn-primary" @click="loadPrices(1)">检索</button>
        </div>
        <div class="filter-item" style="margin-left:auto">
          <label>&nbsp;</label>
          <button class="btn btn-primary" @click="openForm()">+ 录入行情</button>
        </div>
      </div>
    </div>

    <div class="card">
      <div v-if="prices.length === 0" class="empty-state">
        <p>暂无行情记录</p>
        <p style="font-size:13px">挂二手前可先录入千岛/闲鱼成交价作参考</p>
      </div>
      <table v-else>
        <thead>
          <tr>
            <th>款式 ID</th>
            <th>平台</th>
            <th>成交价</th>
            <th>记录日期</th>
            <th>备注</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in prices" :key="p.id">
            <td><strong>{{ p.style_id }}</strong></td>
            <td><span class="tag tag-platform">{{ p.platform }}</span></td>
            <td>¥{{ p.deal_price?.toFixed(2) }}</td>
            <td>{{ p.record_date }}</td>
            <td>{{ p.notes || '-' }}</td>
            <td>
              <div class="actions-cell">
                <button class="btn btn-secondary btn-sm" @click="openForm(p)">编辑</button>
                <button class="btn btn-danger btn-sm" @click="handleDelete(p.id)">删除</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <div class="pagination" v-if="total > 0">
        <button :disabled="page <= 1" @click="loadPrices(page - 1)">上一页</button>
        <span class="page-info">第 {{ page }} / {{ totalPages }} 页 · 共 {{ total }} 条</span>
        <button :disabled="page >= totalPages" @click="loadPrices(page + 1)">下一页</button>
      </div>
    </div>

    <div v-if="showForm" class="modal-overlay" @click.self="showForm = false">
      <div class="modal">
        <div class="modal-title">{{ editing ? '编辑行情' : '录入行情' }}</div>
        <div class="form-row">
          <div class="form-group">
            <label>款式 ID *</label>
            <input v-model="form.style_id" placeholder="与藏品档案款式 ID 一致" />
          </div>
          <div class="form-group">
            <label>平台 *</label>
            <select v-model="form.platform">
              <option value="闲鱼">闲鱼</option>
              <option value="千岛">千岛</option>
              <option value="线下">线下</option>
            </select>
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>成交价 *</label>
            <input v-model.number="form.deal_price" type="number" step="0.01" min="0.01" />
          </div>
          <div class="form-group">
            <label>记录日期 *</label>
            <input v-model="form.record_date" type="date" />
          </div>
        </div>
        <div class="form-group">
          <label>备注</label>
          <textarea v-model="form.notes" rows="2" placeholder="如：九成新盒损"></textarea>
        </div>
        <div v-if="formError" class="form-error">{{ formError }}</div>
        <div class="modal-actions">
          <button class="btn btn-secondary" @click="showForm = false">取消</button>
          <button class="btn btn-primary" @click="handleSubmit">{{ editing ? '保存' : '创建' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { marketApi } from '../api'

const prices = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 10
const filters = ref({ style_id: '', date_from: '', date_to: '' })
const showForm = ref(false)
const editing = ref(null)
const formError = ref('')
const form = ref(getEmptyForm())

function getEmptyForm() {
  return {
    style_id: '',
    platform: '闲鱼',
    deal_price: 0,
    record_date: new Date().toISOString().slice(0, 10),
    notes: '',
  }
}

const totalPages = computed(() => Math.ceil(total.value / pageSize))

async function loadPrices(p = 1) {
  page.value = p
  const params = { page: p, page_size: pageSize }
  if (filters.value.style_id) params.style_id = filters.value.style_id
  if (filters.value.date_from) params.date_from = filters.value.date_from
  if (filters.value.date_to) params.date_to = filters.value.date_to
  const { data } = await marketApi.list(params)
  prices.value = data.prices
  total.value = data.total
}

function openForm(row = null) {
  editing.value = row
  formError.value = ''
  form.value = row ? { ...row } : getEmptyForm()
  showForm.value = true
}

async function handleSubmit() {
  formError.value = ''
  if (!form.value.style_id || !form.value.deal_price || !form.value.record_date) {
    formError.value = '款式 ID、成交价、记录日期为必填'
    return
  }
  try {
    if (editing.value) {
      await marketApi.update(editing.value.id, form.value)
    } else {
      await marketApi.create(form.value)
    }
    showForm.value = false
    await loadPrices(page.value)
  } catch (err) {
    formError.value = err.response?.data?.detail || '操作失败'
  }
}

async function handleDelete(id) {
  if (!confirm('确定删除该行情记录？')) return
  await marketApi.remove(id)
  await loadPrices(page.value)
}

onMounted(() => loadPrices(1))
</script>

<style scoped>
.tag-platform { background: #e8f4fd; color: #2980b9; }
.form-error { color: #e74c3c; font-size: 13px; margin-bottom: 12px; }
</style>
