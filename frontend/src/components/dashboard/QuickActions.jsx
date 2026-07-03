import { Link } from 'react-router-dom'
import Card from '../ui/Card.jsx'
import Button from '../ui/Button.jsx'

const ACTION_CONFIG = {
  complete_onboarding: { label: 'Finish onboarding', to: '/onboarding' },
  generate_workout_plan: { label: 'Generate workout plan', disabled: true },
  generate_nutrition_plan: { label: 'Generate nutrition plan', disabled: true },
  view_profile: { label: 'View profile', to: '/profile' },
  edit_settings: { label: 'Edit settings', to: '/settings' },
}

export default function QuickActions({ actions }) {
  return (
    <Card>
      <h3 className="text-label-lg font-display text-on-surface mb-md">Quick Actions</h3>
      <div className="flex flex-wrap gap-sm">
        {actions.map((key) => {
          const config = ACTION_CONFIG[key]
          if (!config) return null
          if (config.disabled) {
            return (
              <Button key={key} variant="ghost" className="h-10 px-md" disabled>
                {config.label}
              </Button>
            )
          }
          return (
            <Link key={key} to={config.to}>
              <Button variant="secondary" className="h-10 px-md">
                {config.label}
              </Button>
            </Link>
          )
        })}
      </div>
    </Card>
  )
}
