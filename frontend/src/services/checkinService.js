import api from './api'

export async function saveCheckIn(payload) {
  const { data } = await api.post('/checkin', payload)
  return data
}

export async function getTodayCheckIn() {
  try {
    const { data } = await api.get('/checkin/today')
    return data
  } catch (err) {
    if (err.response?.status === 404) return null
    throw err
  }
}

export async function getCheckInHistory() {
  const { data } = await api.get('/checkin/history')
  return data
}
