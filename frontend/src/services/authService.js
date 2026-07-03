import api from './api'

export async function signup({ fullName, email, password }) {
  const { data } = await api.post('/auth/signup', {
    full_name: fullName,
    email,
    password,
  })
  return data
}

export async function login({ email, password }) {
  const { data } = await api.post('/auth/login', { email, password })
  return data
}

export async function forgotPassword(email) {
  const { data } = await api.post('/auth/forgot-password', { email })
  return data
}

export async function getCurrentUser() {
  const { data } = await api.get('/auth/me')
  return data
}
