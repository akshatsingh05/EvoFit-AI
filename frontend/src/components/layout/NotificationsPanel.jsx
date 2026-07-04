import { useState, useRef, useEffect } from 'react'
import { Bell } from 'lucide-react'
import * as notificationService from '../../services/notificationService'

const TYPE_ICON = {
  workout_reminder: '◆',
  meal_reminder: '◐',
  workout_completed: '✓',
  goal_achieved: '★',
  profile_updated: '●',
}

function timeAgo(isoDate) {
  const diffMs = Date.now() - new Date(isoDate).getTime()
  const minutes = Math.floor(diffMs / 60000)
  if (minutes < 1) return 'just now'
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  return `${Math.floor(hours / 24)}d ago`
}

export default function NotificationsPanel() {
  const [open, setOpen] = useState(false)
  const [notifications, setNotifications] = useState([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [loaded, setLoaded] = useState(false)
  const ref = useRef(null)

  const refresh = async () => {
    try {
      const [list, count] = await Promise.all([
        notificationService.listNotifications(),
        notificationService.getUnreadCount(),
      ])
      setNotifications(list)
      setUnreadCount(count)
    } finally {
      setLoaded(true)
    }
  }

  useEffect(() => {
    refresh()
    const interval = setInterval(refresh, 60000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    function handleClickOutside(e) {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false)
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleOpen = () => {
    setOpen((o) => !o)
  }

  const handleMarkAllRead = async () => {
    await notificationService.markAllRead()
    refresh()
  }

  const handleItemClick = async (notification) => {
    if (!notification.is_read) {
      await notificationService.markRead(notification.id)
      refresh()
    }
  }

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={handleOpen}
        className="relative h-9 w-9 rounded-full flex items-center justify-center text-on-surface-variant hover:bg-surface-container"
        aria-label="Notifications"
      >
        <Bell size={18} />
        {unreadCount > 0 ? (
          <span className="absolute top-1 right-1 h-4 w-4 rounded-full bg-error text-on-error text-[10px] flex items-center justify-center">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        ) : null}
      </button>

      {open ? (
        <div className="absolute right-0 mt-sm w-[320px] max-h-[400px] overflow-y-auto bg-surface-container-lowest rounded-md shadow-elevated py-sm z-40">
          <div className="flex items-center justify-between px-md py-sm border-b border-divider mb-xs">
            <span className="text-label-md text-on-surface">Notifications</span>
            {unreadCount > 0 ? (
              <button onClick={handleMarkAllRead} className="text-body-sm text-secondary">
                Mark all read
              </button>
            ) : null}
          </div>

          {loaded && notifications.length === 0 ? (
            <p className="px-md py-md text-body-sm text-on-surface-variant">No notifications yet.</p>
          ) : (
            notifications.map((n) => (
              <button
                key={n.id}
                onClick={() => handleItemClick(n)}
                className={`w-full text-left px-md py-sm flex gap-sm items-start hover:bg-surface-container ${
                  n.is_read ? '' : 'bg-primary/5'
                }`}
              >
                <span className="text-body-md shrink-0 mt-xs" aria-hidden>{TYPE_ICON[n.type] || '•'}</span>
                <span className="flex-1 min-w-0">
                  <span className="block text-body-sm text-on-surface">{n.message}</span>
                  <span className="block text-label-sm text-on-surface-variant mt-xs">{timeAgo(n.created_at)}</span>
                </span>
                {!n.is_read ? <span className="h-2 w-2 rounded-full bg-primary shrink-0 mt-xs" /> : null}
              </button>
            ))
          )}
        </div>
      ) : null}
    </div>
  )
}
