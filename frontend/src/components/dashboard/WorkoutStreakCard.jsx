import Card from '../ui/Card.jsx'

export default function WorkoutStreakCard({ days }) {
  return (
    <Card>
      <h3 className="text-label-lg font-display text-on-surface mb-sm">Workout Streak</h3>
      <p className="text-headline-md text-tertiary">
        {days}
        <span className="text-body-md text-on-surface-variant"> {days === 1 ? 'day' : 'days'}</span>
      </p>
      {days === 0 ? (
        <p className="text-body-sm text-on-surface-variant mt-xs">Complete your first workout to start a streak.</p>
      ) : null}
    </Card>
  )
}
