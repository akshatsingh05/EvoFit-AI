import api from './api'

export async function generateInsight() {
  const { data } = await api.post('/adaptive/generate')
  return data
}

export async function getLatestInsight() {
  const { data } = await api.get('/adaptive/latest')
  return data
}

export async function getInsightHistory() {
  const { data } = await api.get('/adaptive/history')
  return data
}
