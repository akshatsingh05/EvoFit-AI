import axios from 'axios'

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const api = axios.create({ baseURL })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('evofit_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

function clearSession() {
  localStorage.removeItem('evofit_token')
  localStorage.removeItem('evofit_refresh_token')
}

function redirectToLogin() {
  if (window.location.pathname !== '/login') {
    window.location.href = '/login'
  }
}

// When multiple requests 401 at once (e.g. a page fires several calls in
// parallel), only the first should trigger a refresh; the rest wait for
// that same in-flight refresh instead of each racing to rotate the token.
let refreshPromise = null

function performRefresh() {
  const refreshToken = localStorage.getItem('evofit_refresh_token')
  if (!refreshToken) {
    return Promise.reject(new Error('No refresh token available'))
  }

  if (!refreshPromise) {
    refreshPromise = axios
      .post(`${baseURL}/auth/refresh`, { refresh_token: refreshToken })
      .then(({ data }) => {
        localStorage.setItem('evofit_token', data.access_token)
        localStorage.setItem('evofit_refresh_token', data.refresh_token)
        return data.access_token
      })
      .finally(() => {
        refreshPromise = null
      })
  }
  return refreshPromise
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const { config, response } = error
    const isAuthEndpoint = config?.url?.startsWith('/auth/login') || config?.url?.startsWith('/auth/signup') || config?.url?.startsWith('/auth/refresh')

    if (response?.status === 401 && !config._retry && !isAuthEndpoint) {
      config._retry = true
      try {
        const newAccessToken = await performRefresh()
        config.headers.Authorization = `Bearer ${newAccessToken}`
        return api(config)
      } catch {
        clearSession()
        redirectToLogin()
        return Promise.reject(error)
      }
    }

    if (response?.status === 401 && isAuthEndpoint) {
      clearSession()
    }

    return Promise.reject(error)
  }
)

export default api
export { clearSession }
