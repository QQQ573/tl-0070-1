<template>
  <div class="app">
    <header class="app-header">
      <div class="header-inner">
        <h1 class="logo" @click="$router.push('/')">🧸 Labubu 藏品管理</h1>
        <nav class="nav">
          <router-link to="/dashboard" class="nav-link" active-class="active">资产总览</router-link>
          <router-link to="/items" class="nav-link" active-class="active">藏品档案</router-link>
          <router-link to="/exchanges" class="nav-link" active-class="active">置换记录</router-link>
          <router-link to="/market" class="nav-link" active-class="active">行情参考</router-link>
          <router-link to="/recycle" class="nav-link" active-class="active">回收站</router-link>
        </nav>
      </div>
    </header>
    <main class="app-main">
      <router-view />
    </main>
  </div>
</template>

<script setup>
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Noto Sans SC', sans-serif;
  background: #f5f0eb;
  color: #2c2420;
  line-height: 1.6;
}

.app {
  min-height: 100vh;
}

.app-header {
  background: linear-gradient(135deg, #6b4c3b, #8b6f5c);
  color: #fff;
  box-shadow: 0 2px 12px rgba(107, 76, 59, 0.3);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
}

.logo {
  font-size: 20px;
  cursor: pointer;
  letter-spacing: 1px;
}

.nav {
  display: flex;
  gap: 8px;
}

.nav-link {
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  padding: 8px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.nav-link:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.15);
}

.nav-link.active {
  color: #fff;
  background: rgba(255, 255, 255, 0.25);
}

.app-main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 1px 8px rgba(0, 0, 0, 0.06);
  padding: 24px;
  margin-bottom: 20px;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 16px;
  color: #3d2e25;
}

.btn {
  padding: 8px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn-primary {
  background: #6b4c3b;
  color: #fff;
}

.btn-primary:hover {
  background: #5a3f31;
}

.btn-danger {
  background: #e74c3c;
  color: #fff;
}

.btn-danger:hover {
  background: #c0392b;
}

.btn-secondary {
  background: #e8ddd5;
  color: #3d2e25;
}

.btn-secondary:hover {
  background: #d9cdc3;
}

.btn-sm {
  padding: 5px 12px;
  font-size: 13px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 6px;
  color: #5a4a3f;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1.5px solid #d9cdc3;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.2s;
  background: #faf8f6;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #6b4c3b;
  box-shadow: 0 0 0 3px rgba(107, 76, 59, 0.1);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.tag {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.tag-hidden {
  background: #ffeaa7;
  color: #d68910;
}

.tag-limited {
  background: #d5f5e3;
  color: #27ae60;
}

.tag-normal {
  background: #d6eaf8;
  color: #2980b9;
}

.tag-instock {
  background: #d5f5e3;
  color: #27ae60;
}

.tag-out {
  background: #fadbd8;
  color: #e74c3c;
}

.tag-exchanging {
  background: #ffeaa7;
  color: #d68910;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 20px;
}

.pagination button {
  padding: 6px 14px;
  border: 1.5px solid #d9cdc3;
  border-radius: 8px;
  background: #fff;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}

.pagination button:hover:not(:disabled) {
  border-color: #6b4c3b;
  background: #faf8f6;
}

.pagination button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.pagination .page-info {
  font-size: 13px;
  color: #8b7e74;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}

.modal {
  background: #fff;
  border-radius: 16px;
  padding: 28px;
  width: 90%;
  max-width: 600px;
  max-height: 85vh;
  overflow-y: auto;
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.15);
}

.modal-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 20px;
  color: #3d2e25;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 24px;
}

table {
  width: 100%;
  border-collapse: collapse;
}

table th {
  text-align: left;
  padding: 10px 12px;
  font-size: 12px;
  font-weight: 600;
  color: #8b7e74;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 2px solid #e8ddd5;
}

table td {
  padding: 10px 12px;
  font-size: 14px;
  border-bottom: 1px solid #f0e8e0;
}

table tr:hover td {
  background: #faf8f6;
}

.actions-cell {
  display: flex;
  gap: 6px;
}

.empty-state {
  text-align: center;
  padding: 48px 20px;
  color: #8b7e74;
}

.empty-state p {
  font-size: 16px;
  margin-bottom: 8px;
}

.filter-bar {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: flex-end;
  margin-bottom: 20px;
}

.filter-bar .filter-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.filter-bar .filter-item label {
  font-size: 12px;
  font-weight: 600;
  color: #8b7e74;
}

.filter-bar .filter-item input,
.filter-bar .filter-item select {
  padding: 7px 12px;
  border: 1.5px solid #d9cdc3;
  border-radius: 8px;
  font-size: 13px;
  background: #faf8f6;
}

.filter-bar .filter-item input:focus,
.filter-bar .filter-item select:focus {
  outline: none;
  border-color: #6b4c3b;
}
</style>
