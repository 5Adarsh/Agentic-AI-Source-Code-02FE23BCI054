import api from './axios'

/**
 * List faculty with optional filters
 */
export const getFaculty = async (params = {}) => {
  const { data } = await api.get('/faculty/', { params })
  return data
}

/**
 * Get a single faculty member by ID
 */
export const getFacultyById = async (id) => {
  const { data } = await api.get(`/faculty/${id}`)
  return data
}

/**
 * Create a new faculty member
 */
export const createFaculty = async (payload) => {
  const { data } = await api.post('/faculty', payload)
  return data
}

/**
 * Update an existing faculty member
 */
export const updateFaculty = async (id, payload) => {
  const { data } = await api.put(`/faculty/${id}`, payload)
  return data
}

/**
 * Delete a faculty member
 */
export const deleteFaculty = async (id) => {
  await api.delete(`/faculty/${id}`)
}

/**
 * Get faculty publications
 */
export const getFacultyPublications = async (id, params = {}) => {
  const { data } = await api.get(`/faculty/${id}/publications`, { params })
  return data
}

/**
 * Get faculty citation metrics
 */
export const getFacultyCitationMetrics = async (id) => {
  const { data } = await api.get(`/faculty/${id}/citation-metrics`)
  return data
}

/**
 * List departments
 */
export const getDepartments = async () => {
  const { data } = await api.get('/departments')
  return data
}
