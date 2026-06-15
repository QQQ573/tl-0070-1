import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

export const itemsApi = {
  list: (params) => api.get('/items', { params }),
  get: (id) => api.get(`/items/${id}`),
  create: (data) => api.post('/items', data),
  update: (id, data) => api.put(`/items/${id}`, data),
  remove: (id) => api.delete(`/items/${id}`),
  series: () => api.get('/items/series'),
}

export const exchangesApi = {
  list: (params) => api.get('/exchanges', { params }),
  get: (id) => api.get(`/exchanges/${id}`),
  create: (data) => api.post('/exchanges', data),
  update: (id, data) => api.put(`/exchanges/${id}`, data),
  remove: (id) => api.delete(`/exchanges/${id}`),
  confirm: (id) => api.post(`/exchanges/${id}/confirm`),
  cancel: (id) => api.post(`/exchanges/${id}/cancel`),
}

export const marketApi = {
  list: (params) => api.get('/market-prices', { params }),
  get: (id) => api.get(`/market-prices/${id}`),
  create: (data) => api.post('/market-prices', data),
  update: (id, data) => api.put(`/market-prices/${id}`, data),
  remove: (id) => api.delete(`/market-prices/${id}`),
  trend: (styleId, params) => api.get(`/market-prices/trend/${encodeURIComponent(styleId)}`, { params }),
}

export const statsApi = {
  dashboard: () => api.get('/stats/dashboard'),
}

export const recycleApi = {
  list: () => api.get('/recycle'),
  restoreItem: (id) => api.post(`/recycle/items/${id}/restore`),
  restoreExchange: (id) => api.post(`/recycle/exchanges/${id}/restore`),
  hardDeleteItem: (id) => api.delete(`/recycle/items/${id}`),
  hardDeleteExchange: (id) => api.delete(`/recycle/exchanges/${id}`),
}

export const uploadsApi = {
  upload: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/uploads', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}

export default api
