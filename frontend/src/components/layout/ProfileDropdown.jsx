import { useState, useRef, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth.js'

export default function ProfileDropdown() {
  const { user, logout } = useAuth()
  const [open, setOpen] = useState(false)
  const ref = useRef(null)

  useEffect(() => {
    function handleClickOutside(e) {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false)
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const initials = (user?.full_name || '?')
    .split(' ')
    .map((p) => p[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen((o) => !o)}
        className="h-10 w-10 rounded-full bg-primary-container flex items-center justify-center text-on-primary-container font-display font-semibold text-label-md"
        aria-label="Open profile menu"
      >
        {initials}
      </button>

      {open ? (
        <div className="absolute right-0 mt-sm w-[220px] bg-surface-container-lowest rounded-md shadow-elevated py-sm z-40">
          <div className="px-md py-sm border-b border-divider mb-xs">
            <p className="text-label-md text-on-surface truncate">{user?.full_name}</p>
            <p className="text-body-sm text-on-surface-variant truncate">{user?.email}</p>
          </div>
          <Link
            to="/profile"
            onClick={() => setOpen(false)}
            className="block px-md h-10 flex items-center text-body-sm text-on-surface hover:bg-surface-container"
          >
            View profile
          </Link>
          <Link
            to="/settings"
            onClick={() => setOpen(false)}
            className="block px-md h-10 flex items-center text-body-sm text-on-surface hover:bg-surface-container"
          >
            Settings
          </Link>
          <button
            onClick={logout}
            className="w-full text-left px-md h-10 flex items-center text-body-sm text-error hover:bg-error-container/30"
          >
            Log out
          </button>
        </div>
      ) : null}
    </div>
  )
}
