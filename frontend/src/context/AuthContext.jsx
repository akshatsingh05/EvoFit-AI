import { createContext, useState, useEffect, useCallback } from 'react'
import * as authService from '../services/authService'
import * as settingsService from '../services/settingsService'
import { useTheme } from './ThemeContext.jsx'

export const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const { syncFromUserSettings } = useTheme()

  const hydrate = useCallback(async () => {
    const token = localStorage.getItem('evofit_token')
    if (!token) {
      setIsLoading(false)
      return
    }
    try {
      const currentUser = await authService.getCurrentUser()
      setUser(currentUser)
    } catch {
      localStorage.removeItem('evofit_token')
      setUser(null)
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    hydrate()
  }, [hydrate])

  // Whenever a user becomes authenticated (initial load, login, or signup),
  // pull their saved theme so it's consistent across devices/browsers —
  // localStorage on this device already applied instantly, this just
  // reconciles if they'd set a different theme somewhere else.
  useEffect(() => {
    if (!user) return
    let cancelled = false
    settingsService
      .getSettings()
      .then((data) => {
        if (!cancelled) syncFromUserSettings(data.theme)
      })
      .catch(() => {})
    return () => {
      cancelled = true
    }
  }, [user, syncFromUserSettings])

  const login = async (credentials) => {
    const data = await authService.login(credentials)
    localStorage.setItem('evofit_token', data.access_token)
    setUser(data.user)
    return data.user
  }

  const signup = async (payload) => {
    const data = await authService.signup(payload)
    localStorage.setItem('evofit_token', data.access_token)
    setUser(data.user)
    return data.user
  }

  const logout = () => {
    localStorage.removeItem('evofit_token')
    setUser(null)
  }

  const updateUser = (patch) => {
    setUser((prev) => (prev ? { ...prev, ...patch } : prev))
  }

  return (
    <AuthContext.Provider value={{ user, isLoading, login, signup, logout, updateUser }}>
      {children}
    </AuthContext.Provider>
  )
}
