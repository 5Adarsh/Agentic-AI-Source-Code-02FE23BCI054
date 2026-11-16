import api from './axios'

export const verificationApi = {
  getVerifications: (params) => api.get('/verification/', { params }),
  getVerification: (publicationId) => api.get(`/verification/${publicationId}`),
  submitManualVerification: (publicationId, payload) =>
    api.post(`/verification/${publicationId}/manual`, payload),
}

export default verificationApi
