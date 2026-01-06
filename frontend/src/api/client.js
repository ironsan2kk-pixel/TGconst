import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if needed
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

// Dashboard
export const dashboardAPI = {
  getStats: () => api.get('/dashboard/stats'),
  getChartData: (days = 30) => api.get(`/dashboard/chart?days=${days}`),
  getRecentEvents: (limit = 10) => api.get(`/dashboard/recent?limit=${limit}`),
}

// Channels
export const channelsAPI = {
  getAll: () => api.get('/channels'),
  getById: (id) => api.get(`/channels/${id}`),
  create: (data) => api.post('/channels', data),
  update: (id, data) => api.put(`/channels/${id}`, data),
  delete: (id) => api.delete(`/channels/${id}`),
}

// Tariffs
export const tariffsAPI = {
  getAll: () => api.get('/tariffs'),
  getById: (id) => api.get(`/tariffs/${id}`),
  create: (data) => api.post('/tariffs', data),
  update: (id, data) => api.put(`/tariffs/${id}`, data),
  delete: (id) => api.delete(`/tariffs/${id}`),
}

// Users
export const usersAPI = {
  getAll: (params) => api.get('/users', { params }),
  getById: (id) => api.get(`/users/${id}`),
  search: (query) => api.get(`/users/search?q=${query}`),
  ban: (id, reason) => api.post(`/users/${id}/ban`, { reason }),
  unban: (id) => api.post(`/users/${id}/unban`),
  grantAccess: (id, data) => api.post(`/users/${id}/grant`, data),
  revokeAccess: (id, subscriptionId) => api.post(`/users/${id}/revoke`, { subscription_id: subscriptionId }),
  export: (format = 'csv') => api.get(`/users/export?format=${format}`, { responseType: 'blob' }),
}

// Subscriptions
export const subscriptionsAPI = {
  getAll: (params) => api.get('/subscriptions', { params }),
  getById: (id) => api.get(`/subscriptions/${id}`),
  getByUser: (userId) => api.get(`/subscriptions/user/${userId}`),
  cancel: (id) => api.post(`/subscriptions/${id}/cancel`),
  extend: (id, days) => api.post(`/subscriptions/${id}/extend`, { days }),
}

// Payments
export const paymentsAPI = {
  getAll: (params) => api.get('/payments', { params }),
  getById: (id) => api.get(`/payments/${id}`),
  confirmManual: (id) => api.post(`/payments/${id}/confirm`),
  createManual: (data) => api.post('/payments/manual', data),
  export: (format = 'csv') => api.get(`/payments/export?format=${format}`, { responseType: 'blob' }),
}

// Promocodes
export const promocodesAPI = {
  getAll: () => api.get('/promocodes'),
  getById: (id) => api.get(`/promocodes/${id}`),
  create: (data) => api.post('/promocodes', data),
  update: (id, data) => api.put(`/promocodes/${id}`, data),
  delete: (id) => api.delete(`/promocodes/${id}`),
  getUsage: (id) => api.get(`/promocodes/${id}/usage`),
}

// Broadcasts
export const broadcastsAPI = {
  getAll: () => api.get('/broadcasts'),
  getById: (id) => api.get(`/broadcasts/${id}`),
  create: (data) => api.post('/broadcasts', data),
  start: (id) => api.post(`/broadcasts/${id}/start`),
  pause: (id) => api.post(`/broadcasts/${id}/pause`),
  resume: (id) => api.post(`/broadcasts/${id}/resume`),
  cancel: (id) => api.post(`/broadcasts/${id}/cancel`),
  delete: (id) => api.delete(`/broadcasts/${id}`),
}

// Menu Builder
export const menuAPI = {
  getAll: () => api.get('/menu'),
  getTree: () => api.get('/menu/tree'),
  getById: (id) => api.get(`/menu/${id}`),
  create: (data) => api.post('/menu', data),
  update: (id, data) => api.put(`/menu/${id}`, data),
  delete: (id) => api.delete(`/menu/${id}`),
  reorder: (items) => api.post('/menu/reorder', { items }),
}

// FAQ
export const faqAPI = {
  getAll: () => api.get('/faq'),
  getById: (id) => api.get(`/faq/${id}`),
  create: (data) => api.post('/faq', data),
  update: (id, data) => api.put(`/faq/${id}`, data),
  delete: (id) => api.delete(`/faq/${id}`),
}

// Settings
export const settingsAPI = {
  getAll: () => api.get('/settings'),
  get: (key) => api.get(`/settings/${key}`),
  update: (key, value) => api.put(`/settings/${key}`, { value }),
  updateBatch: (settings) => api.put('/settings', settings),
}

// Backup
export const backupAPI = {
  getList: () => api.get('/backup'),
  create: () => api.post('/backup/create'),
  download: (filename) => api.get(`/backup/download/${filename}`, { responseType: 'blob' }),
  restore: (filename) => api.post(`/backup/restore/${filename}`),
  delete: (filename) => api.delete(`/backup/${filename}`),
}

export default api
