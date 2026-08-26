import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'https://ayurvedic-traceability-1.onrender.com/api',
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('vt_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('vt_token')
      localStorage.removeItem('vt_session')
      if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export const authService = {
  login: (credentials) => api.post('/auth/login', credentials).then((response) => response.data),
  register: (payload) => api.post('/auth/register', payload).then((response) => response.data),
  save: (data) => {
    localStorage.setItem('vt_token', data.access_token)
    localStorage.setItem('vt_session', JSON.stringify(data.user || data))
  },
  session: () => {
    try { return JSON.parse(localStorage.getItem('vt_session')) } catch { return null }
  },
  logout: () => {
    localStorage.removeItem('vt_token')
    localStorage.removeItem('vt_session')
  },
}

export const userService = { list: () => api.get('/users'), create: (payload) => api.post('/users', payload) }
export const batchService = { get: (id) => api.get(`/batches/${id}`), list: (search = '') => api.get('/batches', { params: search ? { search } : {} }), create: (payload) => api.post('/batches', payload) }
export const custodyService = { 
  listIncoming: () => api.get('/transfers/incoming'), 
  listHistory: () => api.get('/transfers/history'),
  transfer: (id, payload) => api.post(`/transfers/batch/${id}`, payload),
  accept: (transferId) => api.post(`/transfers/${transferId}/accept`),
  reject: (transferId) => api.post(`/transfers/${transferId}/reject`)
}
export const processingService = {
  process: (batchId, payload) => api.post(`/processing/batch/${batchId}`, payload),
  history: (batchId) => api.get(`/processing/batch/${batchId}`)
}
export const laboratoryService = { 
  reports: (id) => api.get(`/laboratory/batch/${id}`),
  addReport: (id, payload) => api.post(`/laboratory/batch/${id}`, payload)
}
export const productService = { 
  get: (id) => api.get(`/products/${id}`), 
  list: () => api.get('/products'),
  create: (payload) => api.post('/products', payload)
}
export const verificationService = { lookup: (identifier) => api.get(`/public/verify/${identifier}`) }
export const adminService = { verifications: () => api.get('/admin/verifications'), approve: (id) => api.post(`/admin/verifications/${id}/approve`), reject: (id, reason) => api.post(`/admin/verifications/${id}/reject`, null, { params: { reason } }) }
export const recallService = { list: () => api.get('/recalls') }
export { api }
