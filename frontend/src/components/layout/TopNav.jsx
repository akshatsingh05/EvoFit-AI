import ProfileDropdown from './ProfileDropdown.jsx'
import NotificationsPanel from './NotificationsPanel.jsx'

export default function TopNav({ onMenuClick, title }) {
  return (
    <header className="sticky top-0 z-10 h-[64px] bg-surface-container-lowest border-b border-divider px-container flex items-center justify-between">
      <div className="flex items-center gap-md">
        <button
          onClick={onMenuClick}
          className="md:hidden h-9 w-9 rounded-md flex items-center justify-center text-on-surface hover:bg-surface-container"
          aria-label="Open menu"
        >
          ☰
        </button>
        <h2 className="text-label-lg font-display text-on-surface">{title}</h2>
      </div>

      <div className="flex items-center gap-md">
        <NotificationsPanel />
        <ProfileDropdown />
      </div>
    </header>
  )
}
