import api from './api'

export async function getReport(period) {
  const { data } = await api.get(`/reports/${period}`)
  return data
}
