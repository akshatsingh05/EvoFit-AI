import { Link } from 'react-router-dom'
import { ClipboardCheck, Bell } from 'lucide-react'
import Card from '../ui/Card.jsx'
import Button from '../ui/Button.jsx'

export default function CheckInStatusBanner({ hasCheckedInToday, unreadNotificationsCount }) {
  if (hasCheckedInToday && unreadNotificationsCount === 0) return null

  return (
    <div className="flex flex-col sm:flex-row gap-md">
      {!hasCheckedInToday ? (
        <Card className="flex-1 flex items-center justify-between gap-md">
          <div className="flex items-center gap-md">
            <ClipboardCheck size={20} className="text-primary shrink-0" aria-hidden />
            <p className="text-body-sm text-on-surface">You haven't checked in today yet.</p>
          </div>
          <Link to="/checkin">
            <Button variant="primary" className="h-9 px-md shrink-0">Check in</Button>
          </Link>
        </Card>
      ) : null}

      {unreadNotificationsCount > 0 ? (
        <Card className="flex-1 flex items-center gap-md">
          <Bell size={20} className="text-secondary shrink-0" aria-hidden />
          <p className="text-body-sm text-on-surface">
            You have {unreadNotificationsCount} unread notification{unreadNotificationsCount === 1 ? '' : 's'}.
          </p>
        </Card>
      ) : null}
    </div>
  )
}
