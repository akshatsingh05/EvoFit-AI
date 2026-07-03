import Card from '../ui/Card.jsx'
import Button from '../ui/Button.jsx'

export default function TodayWorkoutCard({ workout }) {
  return (
    <Card>
      <div className="flex items-center justify-between mb-sm">
        <h3 className="text-label-lg font-display text-on-surface">Today's Workout</h3>
        <span className="text-lg">◆</span>
      </div>

      {workout.status === 'not_generated' ? (
        <>
          <p className="text-body-sm text-on-surface-variant mb-md">
            No workout plan yet — this is built by the AI generation engine in Module 3.
          </p>
          <Button variant="secondary" className="h-10 px-md" disabled>
            Generate plan (coming soon)
          </Button>
        </>
      ) : (
        <>
          <p className="text-body-md text-on-surface">{workout.title}</p>
          <p className="text-body-sm text-on-surface-variant">{workout.exercise_count} exercises</p>
        </>
      )}
    </Card>
  )
}
