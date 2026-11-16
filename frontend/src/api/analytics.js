import api from './axios'

/**
 * Get institutional dashboard metrics
 */
export const getDashboardMetrics = async () => {
  const { data } = await api.get('/analytics/dashboard')
  return data
}

/**
 * Get citation trends (year → total citations)
 */
export const getCitationTrends = async (params = {}) => {
  const { data } = await api.get('/analytics/citation-trends', { params })
  return data
}

/**
 * Get publications per year
 */
export const getPublicationsByYear = async (params = {}) => {
  const { data } = await api.get('/analytics/publications-by-year', { params })
  return data
}

/**
 * Get h-index data for faculty or institution
 */
export const getHIndexData = async (params = {}) => {
  const { data } = await api.get('/analytics/h-index', { params })
  return data
}

/**
 * Get department comparison metrics
 */
export const getDepartmentComparison = async (params = {}) => {
  const { data } = await api.get('/analytics/department-comparison', { params })
  return data
}

/**
 * Get publication type distribution
 */
export const getPublicationTypeDistribution = async (params = {}) => {
  const { data } = await api.get('/analytics/publication-types', { params })
  return data
}

/**
 * Get top publications by citations
 */
export const getTopPublications = async (params = {}) => {
  const { data } = await api.get('/analytics/top-publications', { params })
  return data
}

/**
 * Get faculty citation metrics (for a specific faculty)
 */
export const getFacultyAnalytics = async (facultyId, params = {}) => {
  const { data } = await api.get(`/analytics/faculty/${facultyId}`, { params })
  return data
}
