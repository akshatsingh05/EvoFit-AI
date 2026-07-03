import { useAuth } from '../hooks/useAuth.js'
import Button from '../components/ui/Button.jsx'
import Card from '../components/ui/Card.jsx'

export default function Dashboard() {
  const { user, logout } = useAuth()

  return (
    <div className="min-h-screen bg-background px-container py-xl">
      <div className="max-w-[720px] mx-auto">
        <div className="flex items-center justify-between mb-xl">
          <div>
            <h1 className="text-headline-md text-on-surface">Welcome, {user?.full_name?.split(' ')[0]}</h1>
            <p className="text-body-md text-on-surface-variant">Your account and onboarding data are live from the backend.</p>
          </div>
          <Button variant="ghost" onClick={logout}>
            Log out
          </Button>
        </div>

        <Card>
          <h2 className="text-headline-sm mb-md">Module 1 complete</h2>
          <ul className="space-y-sm text-body-md text-on-surface-variant">
            <li>✓ Account created and authenticated with JWT ({user?.email})</li>
            <li>✓ Onboarding profile saved to the database</li>
            <li>✓ Medical history recorded</li>
          </ul>
          <p className="mt-md text-body-sm text-on-surface-variant">
            The full Dashboard — sidebar navigation, workout/nutrition overview widgets, recovery score,
            streaks, and the AI coach tip — is built in Module 2, next.
          </p>
        </Card>
      </div>
    </div>
  )
}
