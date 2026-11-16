import api from './axios'

export const systemApi = {
  getConfigStatus: () => api.get('/system/config-status'),
  seedDemo: () => api.post('/system/seed-demo'),
  clearDemo: () => api.post('/system/clear-demo'),
}

export default systemApi
