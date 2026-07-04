import { Link } from 'react-router-dom'
import { Dumbbell } from 'lucide-react'
import Card from '../ui/Card.jsx'
import Button from '../ui/Button.jsx'

export default function TodayWorkoutCard({ workout }) {
  return (
    <Card>
      <div className="flex items-center justify-between mb-sm">
        <h3 className="text-label-lg font-display text-on-surface">Today's Workout</h3>
        <Dumbbell size={18} className="text-on-surface-variant" aria-hidden />
      </div>

      {workout.status === 'not_generated' ? (
        <p className="text-body-sm text-on-surface-variant mb-md">
          Complete onboarding to get your first AI-generated workout plan.
        </p>
      ) : workout.status === 'rest_day' ? (
        <p className="text-body-md text-on-surface-variant mb-md">Rest day — no workout scheduled.</p>
      ) : (
        <>
          <p className="text-body-md text-on-surface capitalize">{workout.title}</p>
          <p className="text-body-sm text-on-surface-variant mb-md">
            {workout.exercise_count} exercises {workout.status === 'completed' ? '· Completed ✓' : ''}
          </p>
        </>
      )}

      <Link to={workout.status === 'not_generated' ? '/onboarding' : '/workout'}>
        <Button variant="secondary" className="h-10 px-md">
          {workout.status === 'not_generated' ? 'Go to onboarding' : 'View workout'}
        </Button>
      </Link>
    </Card>
  )
}
