import api from './api'

export async function listNotifications() {
  const { data } = await api.get('/notifications')
  return data
}

export async function getUnreadCount() {
  const { data } = await api.get('/notifications/unread-count')
  return data.unread_count
}

export async function markRead(notificationId) {
  const { data } = await api.put(`/notifications/${notificationId}/read`)
  return data
}

export async function markAllRead() {
  const { data } = await api.put('/notifications/read-all')
  return data
}
