import Card from '../ui/Card.jsx'
import Button from '../ui/Button.jsx'

export default function TodayNutritionCard({ nutrition }) {
  return (
    <Card>
      <div className="flex items-center justify-between mb-sm">
        <h3 className="text-label-lg font-display text-on-surface">Today's Nutrition</h3>
        <span className="text-lg">◐</span>
      </div>

      {nutrition.status === 'not_generated' ? (
        <>
          <p className="text-body-sm text-on-surface-variant mb-md">
            No meal plan yet — nutrition generation arrives in Module 3.
          </p>
          <Button variant="secondary" className="h-10 px-md" disabled>
            Generate plan (coming soon)
          </Button>
        </>
      ) : (
        <>
          <p className="text-body-md text-on-surface">{nutrition.logged_calories} / {nutrition.target_calories} kcal</p>
        </>
      )}
    </Card>
  )
}
