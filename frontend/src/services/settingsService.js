import api from './api'

export async function getSettings() {
  const { data } = await api.get('/settings')
  return data
}

export async function updateSettings(payload) {
  const { data } = await api.put('/settings', payload)
  return data
}

export async function changePassword({ currentPassword, newPassword }) {
  const { data } = await api.put('/settings/password', {
    current_password: currentPassword,
    new_password: newPassword,
  })
  return data
}
