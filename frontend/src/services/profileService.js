import api from './api'

export async function getProfile() {
  const { data } = await api.get('/profile')
  return data
}

export async function updateProfile({ fullName, email }) {
  const payload = { full_name: fullName }
  if (email) payload.email = email
  const { data } = await api.put('/profile', payload)
  return data
}

export async function deleteAccount() {
  await api.delete('/profile/account')
}
