import { createContext, useContext, useCallback, useState, useRef } from 'react'

const ToastContext = createContext(null)
let idCounter = 0

const VARIANT_STYLES = {
  success: 'bg-primary-container text-on-primary-container',
  error: 'bg-error-container text-on-error-container',
  info: 'bg-surface-container-highest text-on-surface',
}

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])
  const timers = useRef({})

  const dismiss = useCallback((id) => {
    setToasts((current) => current.filter((t) => t.id !== id))
    clearTimeout(timers.current[id])
    delete timers.current[id]
  }, [])

  const showToast = useCallback(
    (message, variant = 'info', duration = 4000) => {
      const id = ++idCounter
      setToasts((current) => [...current, { id, message, variant }])
      timers.current[id] = setTimeout(() => dismiss(id), duration)
      return id
    },
    [dismiss]
  )

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      <div
        className="fixed bottom-lg right-lg z-[100] flex flex-col gap-sm items-end"
        role="region"
        aria-live="polite"
        aria-label="Notifications"
      >
        {toasts.map((t) => (
          <div
            key={t.id}
            role="status"
            className={`
              max-w-[360px] px-md py-sm rounded-md shadow-elevated
              text-body-sm flex items-center gap-md
              animate-[toast-in_0.2s_ease-out]
              ${VARIANT_STYLES[t.variant] || VARIANT_STYLES.info}
            `}
          >
            <span className="flex-1">{t.message}</span>
            <button
              onClick={() => dismiss(t.id)}
              aria-label="Dismiss notification"
              className="text-current opacity-70 hover:opacity-100"
            >
              ✕
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}

export function useToast() {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast must be used within a ToastProvider')
  return ctx
}
