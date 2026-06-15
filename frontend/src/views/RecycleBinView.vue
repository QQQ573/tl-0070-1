<template>
  <div>
    <div class="card hint-card">
      <p>此处展示已软删除的藏品与置换记录。可恢复至正常列表，或永久删除（不可撤销）。</p>
    </div>

    <div class="card">
      <h3 class="section-title">已删除藏品 ({{ items.length }})</h3>
      <div v-if="items.length === 0" class="empty-inline">暂无</div>
      <table v-else>
        <thead>
          <tr>
            <th>系列</th>
            <th>名称</th>
            <th>款式 ID</th>
            <th>删除时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id">
            <td>{{ item.series }}</td>
            <td>{{ item.name }}</td>
            <td>{{ item.style_id }}</td>
            <td>{{ formatTime(item.deleted_at) }}</td>
            <td>
              <div class="actions-cell">
                <button class="btn btn-primary btn-sm" @click="restoreItem(item.id)">恢复</button>
                <button class="btn btn-danger btn-sm" @click="purgeItem(item.id)">永久删除</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="card">
      <h3 class="section-title">已删除置换 ({{ exchanges.length }})</h3>
      <div v-if="exchanges.length === 0" class="empty-inline">暂无</div>
      <table v-else>
        <thead>
          <tr>
            <th>日期</th>
            <th>藏品</th>
            <th>对手方</th>
            <th>删除时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="ex in exchanges" :key="ex.id">
            <td>{{ ex.exchange_date }}</td>
            <td>{{ ex.item_series }} - {{ ex.item_name }}</td>
            <td>{{ ex.counterparty }}</td>
            <td>{{ formatTime(ex.deleted_at) }}</td>
            <td>
              <div class="actions-cell">
                <button class="btn btn-primary btn-sm" @click="restoreExchange(ex.id)">恢复</button>
                <button class="btn btn-danger btn-sm" @click="purgeExchange(ex.id)">永久删除</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { recycleApi } from '../api'

const items = ref([])
const exchanges = ref([])

function formatTime(t) {
  if (!t) return '-'
  return new Date(t).toLocaleString('zh-CN')
}

async function loadRecycle() {
  const { data } = await recycleApi.list()
  items.value = data.items
  exchanges.value = data.exchanges
}

async function restoreItem(id) {
  await recycleApi.restoreItem(id)
  await loadRecycle()
}

async function restoreExchange(id) {
  await recycleApi.restoreExchange(id)
  await loadRecycle()
}

async function purgeItem(id) {
  if (!confirm('永久删除后无法恢复，确定？')) return
  await recycleApi.hardDeleteItem(id)
  await loadRecycle()
}

async function purgeExchange(id) {
  if (!confirm('永久删除后无法恢复，确定？')) return
  await recycleApi.hardDeleteExchange(id)
  await loadRecycle()
}

onMounted(() => loadRecycle())
</script>

<style scoped>
.hint-card { background: #fff9f0; border-left: 4px solid #d4846a; }
.hint-card p { font-size: 14px; color: #6b5344; }
.section-title { font-size: 15px; margin-bottom: 16px; color: #4a3f38; }
.empty-inline { color: #aaa; font-size: 14px; padding: 12px 0; }
</style>
