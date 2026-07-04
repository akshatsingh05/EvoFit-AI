import { Link } from 'react-router-dom'
import { Salad } from 'lucide-react'
import Card from '../ui/Card.jsx'
import Button from '../ui/Button.jsx'

export default function TodayNutritionCard({ nutrition }) {
  return (
    <Card>
      <div className="flex items-center justify-between mb-sm">
        <h3 className="text-label-lg font-display text-on-surface">Today's Nutrition</h3>
        <Salad size={18} className="text-on-surface-variant" aria-hidden />
      </div>

      {nutrition.status === 'not_generated' ? (
        <p className="text-body-sm text-on-surface-variant mb-md">
          Complete onboarding to get your first AI-generated meal plan.
        </p>
      ) : (
        <p className="text-body-md text-on-surface mb-md">
          {nutrition.logged_calories} / {nutrition.target_calories} kcal logged
        </p>
      )}

      <Link to={nutrition.status === 'not_generated' ? '/onboarding' : '/nutrition'}>
        <Button variant="secondary" className="h-10 px-md">
          {nutrition.status === 'not_generated' ? 'Go to onboarding' : 'View nutrition'}
        </Button>
      </Link>
    </Card>
  )
}
