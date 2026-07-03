import api from './api'

export async function getMedicalHistory() {
  try {
    const { data } = await api.get('/medical-history')
    return data
  } catch (err) {
    if (err.response?.status === 404) return null
    throw err
  }
}

export async function saveMedicalHistory(payload) {
  const { data } = await api.post('/medical-history', payload)
  return data
}
