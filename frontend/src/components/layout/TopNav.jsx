import ProfileDropdown from './ProfileDropdown.jsx'

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
        <button
          className="relative h-9 w-9 rounded-full flex items-center justify-center text-on-surface-variant hover:bg-surface-container"
          aria-label="Notifications"
          title="Notifications coming soon"
        >
          🔔
        </button>
        <ProfileDropdown />
      </div>
    </header>
  )
}
