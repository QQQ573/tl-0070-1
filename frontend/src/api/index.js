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
