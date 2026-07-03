import api from './api'

export async function getProfile() {
  const { data } = await api.get('/profile')
  return data
}

export async function updateProfile({ fullName }) {
  const { data } = await api.put('/profile', { full_name: fullName })
  return data
}
