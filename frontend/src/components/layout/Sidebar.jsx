import { NavLink } from 'react-router-dom'

const NAV_ITEMS = [
  { to: '/dashboard', label: 'Dashboard', icon: '⌂', available: true },
  { to: '/workout', label: 'Workout', icon: '◆', available: false },
  { to: '/nutrition', label: 'Nutrition', icon: '◐', available: false },
  { to: '/progress', label: 'Progress', icon: '▲', available: false },
  { to: '/profile', label: 'Profile', icon: '●', available: true },
  { to: '/settings', label: 'Settings', icon: '◈', available: true },
]

export default function Sidebar({ open, onClose }) {
  return (
    <>
      {open ? (
        <button
          aria-label="Close menu"
          onClick={onClose}
          className="fixed inset-0 bg-inverse-surface/40 z-20 md:hidden"
        />
      ) : null}

      <aside
        className={`
          fixed md:sticky top-0 left-0 h-screen w-[240px] bg-surface-container-lowest
          border-r border-divider flex flex-col z-30
          transition-transform duration-200
          ${open ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
        `}
      >
        <div className="flex items-center gap-sm px-lg h-[64px] border-b border-divider">
          <span className="h-8 w-8 rounded-md bg-primary flex items-center justify-center">
            <span className="text-on-primary font-display font-bold text-body-sm">E</span>
          </span>
          <span className="font-display font-bold text-label-lg text-on-surface">EvoFit AI</span>
        </div>

        <nav className="flex-1 px-md py-lg space-y-xs">
          {NAV_ITEMS.map((item) =>
            item.available ? (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={onClose}
                className={({ isActive }) => `
                  flex items-center gap-md px-md h-11 rounded-md text-label-md font-body transition-colors
                  ${isActive ? 'bg-primary/10 text-primary' : 'text-on-surface-variant hover:bg-surface-container'}
                `}
              >
                <span aria-hidden>{item.icon}</span>
                {item.label}
              </NavLink>
            ) : (
              <div
                key={item.to}
                className="flex items-center justify-between gap-md px-md h-11 rounded-md text-label-md font-body text-on-surface-variant/50 cursor-not-allowed"
                title="Coming soon"
              >
                <span className="flex items-center gap-md">
                  <span aria-hidden>{item.icon}</span>
                  {item.label}
                </span>
                <span className="text-label-sm bg-surface-container-high px-sm rounded-full">Soon</span>
              </div>
            )
          )}
        </nav>
      </aside>
    </>
  )
}
