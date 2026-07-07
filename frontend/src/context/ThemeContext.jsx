import { createContext, useContext, useEffect, useState, useCallback } from 'react'

const ThemeContext = createContext(null)
const STORAGE_KEY = 'evofit-theme'

function getStoredTheme() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    return stored === 'dark' || stored === 'light' ? stored : 'light'
  } catch {
    return 'light'
  }
}

function applyThemeClass(theme) {
  const root = document.documentElement
  if (theme === 'dark') root.classList.add('dark')
  else root.classList.remove('dark')
}

/**
 * App-wide theme provider. Sits above AuthProvider so the Landing/Auth pages
 * (no logged-in user yet) still get the persisted theme. Persistence is
 * localStorage-first (survives refresh/logout/login/browser restart on this
 * device); when a user is logged in, `syncFromUserSettings`/the Settings page
 * also push the choice to `/settings` so it travels across devices.
 */
export function ThemeProvider({ children }) {
  const [theme, setThemeState] = useState(getStoredTheme)

  useEffect(() => {
    applyThemeClass(theme)
  }, [theme])

  const setTheme = useCallback((next) => {
    setThemeState(next)
    try {
      localStorage.setItem(STORAGE_KEY, next)
    } catch {
      // localStorage unavailable (private browsing, etc.) — theme still applies for this session
    }
  }, [])

  // Called once after login/loading /settings, so a theme saved on another
  // device wins over whatever was last used on this one.
  const syncFromUserSettings = useCallback(
    (remoteTheme) => {
      if ((remoteTheme === 'dark' || remoteTheme === 'light') && remoteTheme !== theme) {
        setTheme(remoteTheme)
      }
    },
    [theme, setTheme]
  )

  return (
    <ThemeContext.Provider value={{ theme, setTheme, syncFromUserSettings }}>{children}</ThemeContext.Provider>
  )
}

export function useTheme() {
  const ctx = useContext(ThemeContext)
  if (!ctx) throw new Error('useTheme must be used within a ThemeProvider')
  return ctx
}
