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
          <tr v-for="item in items" :key="item.id">
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
              <div class="actions-cell">
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
import { ref, onMounted, computed } from 'vue'
import { itemsApi, uploadsApi } from '../api'

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
</script>
