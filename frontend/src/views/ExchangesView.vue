<template>
  <div>
    <div class="card">
      <div class="filter-bar">
        <div class="filter-item">
          <label>对手方昵称</label>
          <input v-model="filters.counterparty" placeholder="搜索对手方" @keyup.enter="loadExchanges(1)" />
        </div>
        <div class="filter-item">
          <label>&nbsp;</label>
          <button class="btn btn-primary" @click="loadExchanges(1)">检索</button>
        </div>
        <div class="filter-item" style="margin-left:auto">
          <label>&nbsp;</label>
          <button class="btn btn-primary" @click="openForm()">+ 新增置换记录</button>
        </div>
      </div>
    </div>

    <div class="card">
      <div v-if="exchanges.length === 0" class="empty-state">
        <p>暂无置换记录</p>
        <p style="font-size:13px">点击「新增置换记录」开始添加</p>
      </div>
      <table v-else>
        <thead>
          <tr>
            <th>日期</th>
            <th>藏品系列</th>
            <th>藏品名称</th>
            <th>对手方</th>
            <th>差价</th>
            <th>流转状态</th>
            <th>备注</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="ex in exchanges" :key="ex.id">
            <td>{{ ex.exchange_date }}</td>
            <td>{{ ex.item_series || '-' }}</td>
            <td><strong>{{ ex.item_name || '-' }}</strong></td>
            <td>{{ ex.counterparty }}</td>
            <td :style="{ color: ex.price_difference >= 0 ? '#27ae60' : '#e74c3c' }">
              {{ ex.price_difference >= 0 ? '+' : '' }}¥{{ ex.price_difference?.toFixed(2) }}
            </td>
            <td><span class="tag" :class="flowClass(ex.flow_status)">{{ ex.flow_status || '洽谈中' }}</span></td>
            <td>{{ ex.notes || '-' }}</td>
            <td>
              <div class="actions-cell">
                <template v-if="ex.flow_status === '洽谈中'">
                  <button class="btn btn-primary btn-sm" @click="handleConfirm(ex.id)">成交确认</button>
                  <button class="btn btn-secondary btn-sm" @click="handleCancel(ex.id)">撤回</button>
                  <button class="btn btn-secondary btn-sm" @click="openForm(ex)">编辑</button>
                </template>
                <span v-else class="locked-hint">已锁定</span>
                <button class="btn btn-danger btn-sm" @click="handleDelete(ex.id)">删除</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <div class="pagination" v-if="total > 0">
        <button :disabled="page <= 1" @click="loadExchanges(page - 1)">上一页</button>
        <span class="page-info">第 {{ page }} / {{ totalPages }} 页 · 共 {{ total }} 条</span>
        <button :disabled="page >= totalPages" @click="loadExchanges(page + 1)">下一页</button>
      </div>
    </div>

    <div v-if="showForm" class="modal-overlay" @click.self="showForm = false">
      <div class="modal">
        <div class="modal-title">{{ editingExchange ? '编辑置换记录' : '新增置换记录' }}</div>
        <div class="form-group">
          <label>关联藏品 *</label>
          <select v-model="form.item_id">
            <option v-for="item in allItems" :key="item.id" :value="item.id">
              {{ item.series }} - {{ item.name }} ({{ item.style_id }})
            </option>
          </select>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>置换日期 *</label>
            <input v-model="form.exchange_date" type="date" />
          </div>
          <div class="form-group">
            <label>对手方昵称 *</label>
            <input v-model="form.counterparty" placeholder="对方藏家昵称" />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>差价（正=收到，负=贴出）</label>
            <input v-model.number="form.price_difference" type="number" step="0.01" placeholder="0.00" />
          </div>
        </div>
        <div class="form-group">
          <label>备注</label>
          <textarea v-model="form.notes" rows="2" placeholder="置换备注"></textarea>
        </div>
        <div v-if="formError" style="color:#e74c3c;font-size:13px;margin-bottom:12px;">{{ formError }}</div>
        <div class="modal-actions">
          <button class="btn btn-secondary" @click="showForm = false">取消</button>
          <button class="btn btn-primary" @click="handleSubmit">{{ editingExchange ? '保存' : '创建' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { exchangesApi, itemsApi } from '../api'

const exchanges = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 10
const allItems = ref([])

const filters = ref({ counterparty: '' })

const showForm = ref(false)
const editingExchange = ref(null)
const form = ref(getEmptyForm())
const formError = ref('')

function getEmptyForm() {
  return {
    item_id: null,
    exchange_date: new Date().toISOString().slice(0, 10),
    counterparty: '',
    price_difference: 0,
    notes: '',
  }
}

const totalPages = computed(() => Math.ceil(total.value / pageSize))

async function loadExchanges(p = 1) {
  page.value = p
  const params = { page: p, page_size: pageSize }
  if (filters.value.counterparty) params.counterparty = filters.value.counterparty
  try {
    const { data } = await exchangesApi.list(params)
    exchanges.value = data.exchanges
    total.value = data.total
  } catch (e) {
    console.error(e)
  }
}

async function loadAllItems() {
  try {
    const { data } = await itemsApi.list({ page: 1, page_size: 999 })
    allItems.value = data.items.filter(i => i.status === '在库')
  } catch (e) {
    console.error(e)
  }
}

function flowClass(status) {
  if (status === '已成交') return 'tag-done'
  if (status === '已撤回') return 'tag-cancel'
  return 'tag-pending'
}

async function handleConfirm(id) {
  if (!confirm('确认成交？关联藏品将标记为「已出」且记录锁定。')) return
  try {
    await exchangesApi.confirm(id)
    await loadExchanges(page.value)
    await loadAllItems()
  } catch (err) {
    alert(err.response?.data?.detail || '操作失败')
  }
}

async function handleCancel(id) {
  if (!confirm('撤回置换？关联藏品将恢复「在库」。')) return
  try {
    await exchangesApi.cancel(id)
    await loadExchanges(page.value)
    await loadAllItems()
  } catch (err) {
    alert(err.response?.data?.detail || '操作失败')
  }
}

function openForm(ex = null) {
  editingExchange.value = ex
  formError.value = ''
  if (ex) {
    form.value = {
      item_id: ex.item_id,
      exchange_date: ex.exchange_date,
      counterparty: ex.counterparty,
      price_difference: ex.price_difference,
      notes: ex.notes || '',
    }
  } else {
    form.value = getEmptyForm()
    if (allItems.value.length > 0 && !form.value.item_id) {
      form.value.item_id = allItems.value[0].id
    }
  }
  showForm.value = true
}

async function handleSubmit() {
  formError.value = ''
  if (!form.value.item_id || !form.value.exchange_date || !form.value.counterparty) {
    formError.value = '关联藏品、日期、对手方为必填项'
    return
  }
  try {
    if (editingExchange.value) {
      await exchangesApi.update(editingExchange.value.id, form.value)
    } else {
      await exchangesApi.create(form.value)
    }
    showForm.value = false
    await loadExchanges(page.value)
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
  if (!confirm('确定删除该置换记录？（软删除）')) return
  try {
    await exchangesApi.remove(id)
    await loadExchanges(page.value)
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => {
  loadExchanges(1)
  loadAllItems()
})
</script>

<style scoped>
.tag-done { background: #e8f8ef; color: #27ae60; }
.tag-cancel { background: #f0f0f0; color: #888; }
.tag-pending { background: #fff3e0; color: #e67e22; }
.locked-hint { font-size: 12px; color: #aaa; margin-right: 4px; }
</style>
