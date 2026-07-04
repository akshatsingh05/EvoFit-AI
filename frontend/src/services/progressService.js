import api from './api'

export async function getProgress() {
  const { data } = await api.get('/progress')
  return data
}

export async function logWeight({ logDate, weightKg }) {
  const { data } = await api.post('/progress/weight', { log_date: logDate, weight_kg: weightKg })
  return data
}
