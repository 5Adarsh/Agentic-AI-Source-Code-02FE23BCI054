import api from './axios'

export const duplicatesApi = {
  getDuplicates: (params) => api.get('/duplicates/', { params }),
  resolveDuplicate: (id, payload) => api.post(`/duplicates/${id}/resolve`, payload),
}

export default duplicatesApi
