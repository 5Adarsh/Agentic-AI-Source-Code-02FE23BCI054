import api from './axios'

/**
 * List publications with optional filters and pagination
 */
export const getPublications = async (params = {}) => {
  const { data } = await api.get('/publications/', { params })
  return data
}

/**
 * Get a single publication by ID
 */
export const getPublicationById = async (id) => {
  const { data } = await api.get(`/publications/${id}`)
  return data
}

/**
 * Create a publication manually
 */
export const createPublication = async (payload) => {
  const { data } = await api.post('/publications', payload)
  return data
}

/**
 * Update a publication
 */
export const updatePublication = async (id, payload) => {
  const { data } = await api.put(`/publications/${id}`, payload)
  return data
}

/**
 * Delete a publication
 */
export const deletePublication = async (id) => {
  await api.delete(`/publications/${id}`)
}

/**
 * Import publications via Scholar CSV upload
 */
export const importScholarCSV = async (facultyId, file, onUploadProgress) => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('faculty_id', facultyId)

  const { data } = await api.post('/publications/import/scholar-csv', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress,
  })
  return data
}

/**
 * Get duplicate candidates for a publication
 */
export const getDuplicateCandidates = async (id) => {
  const { data } = await api.get(`/publications/${id}/duplicates`)
  return data
}

/**
 * Resolve duplicate — keep or discard
 */
export const resolveDuplicate = async (id, payload) => {
  const { data } = await api.post(`/publications/${id}/duplicates/resolve`, payload)
  return data
}

/**
 * Get publication verification sources
 */
export const getPublicationSources = async (id) => {
  const { data } = await api.get(`/publications/${id}/sources`)
  return data
}

/**
 * Update verification status
 */
export const updateVerificationStatus = async (id, payload) => {
  const { data } = await api.patch(`/publications/${id}/verification`, payload)
  return data
}
