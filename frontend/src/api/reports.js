import api from './axios'

export const getReports = async (params = {}) => {
  const { data } = await api.get('/reports/', { params })
  return data
}

export const getReportById = async (id) => {
  const { data } = await api.get(`/reports/${id}`)
  return data
}

export const generateReport = async (payload) => {
  if (payload.report_type === 'nirf') {
    const { data } = await api.post('/reports/nirf', payload)
    return data
  } else if (payload.report_type === 'naac') {
    const { data } = await api.post('/reports/naac', payload)
    return data
  }
  const { data } = await api.post('/reports/', payload)
  return data
}

export const downloadPdfReport = async (reportId, filename = `report_${reportId}.pdf`) => {
  const response = await api.get(`/reports/${reportId}/download/pdf`, {
    responseType: 'blob',
  })
  const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', filename)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

export const downloadExcelReport = async (reportId, filename = `report_${reportId}.xlsx`) => {
  const response = await api.get(`/reports/${reportId}/download/excel`, {
    responseType: 'blob',
  })
  const url = window.URL.createObjectURL(
    new Blob([response.data], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    })
  )
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', filename)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

export const downloadReport = downloadPdfReport
