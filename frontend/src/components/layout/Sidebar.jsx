import { NavLink } from 'react-router-dom'
import { LayoutDashboard, Dumbbell, Salad, TrendingUp, ClipboardCheck, User, Settings as SettingsIcon } from 'lucide-react'
import logo from '../../assets/logo.png'

const NAV_ITEMS = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/workout', label: 'Workout', icon: Dumbbell },
  { to: '/nutrition', label: 'Nutrition', icon: Salad },
  { to: '/checkin', label: 'Daily Check-In', icon: ClipboardCheck },
  { to: '/progress', label: 'Progress', icon: TrendingUp },
  { to: '/profile', label: 'Profile', icon: User },
  { to: '/settings', label: 'Settings', icon: SettingsIcon },
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
          <img src={logo} alt="EvoFit AI" className="h-8 w-8 rounded-md object-cover" />
          <span className="font-display font-bold text-label-lg text-on-surface">EvoFit AI</span>
        </div>

        <nav className="flex-1 px-md py-lg space-y-xs">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon
            return (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={onClose}
                className={({ isActive }) => `
                  flex items-center gap-md px-md h-11 rounded-md text-label-md font-body transition-colors
                  ${isActive ? 'bg-primary/10 text-primary' : 'text-on-surface-variant hover:bg-surface-container'}
                `}
              >
                <Icon size={18} aria-hidden="true" />
                {item.label}
              </NavLink>
            )
          })}
        </nav>
      </aside>
    </>
  )
}
