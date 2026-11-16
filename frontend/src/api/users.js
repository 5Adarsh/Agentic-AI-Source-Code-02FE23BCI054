import api from './axios'

export const usersApi = {
  getUsers: (params = {}) => api.get('/users/', { params }),
  createUser: (payload) => api.post('/users/', payload),
  updateUser: (id, payload) => api.patch(`/users/${id}`, payload),
  deleteUser: (id) => api.delete(`/users/${id}`),
}

export default usersApi
