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

export async function logout(refreshToken) {
  if (!refreshToken) return
  // Best-effort: even if this fails (e.g. token already expired/offline),
  // the caller always clears local session state.
  try {
    await api.post('/auth/logout', { refresh_token: refreshToken })
  } catch {
    // no-op: session is cleared client-side regardless
  }
}

export async function forgotPassword(email) {
  const { data } = await api.post('/auth/forgot-password', { email })
  return data
}

export async function getCurrentUser() {
  const { data } = await api.get('/auth/me')
  return data
}
