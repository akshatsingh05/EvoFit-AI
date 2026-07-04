import Button from '../ui/Button.jsx'

const MEAL_LABELS = { breakfast: 'Breakfast', lunch: 'Lunch', snack: 'Snack', dinner: 'Dinner' }

export default function MealCard({ meal, status, onSetStatus, saving }) {
  return (
    <div className="py-md border-b border-divider last:border-none">
      <div className="flex items-center justify-between mb-xs">
        <span className="text-label-sm text-on-surface-variant uppercase tracking-wide">
          {MEAL_LABELS[meal.meal_type] || meal.meal_type}
        </span>
        {status ? (
          <span
            className={`text-label-sm px-sm h-6 rounded-full flex items-center ${
              status === 'completed' ? 'bg-primary/10 text-primary' : 'bg-surface-container-high text-on-surface-variant'
            }`}
          >
            {status === 'completed' ? 'Completed' : 'Skipped'}
          </span>
        ) : null}
      </div>
      <h4 className="text-label-lg font-display text-on-surface mb-xs">{meal.name}</h4>
      <div className="flex flex-wrap gap-md text-body-sm text-on-surface-variant mb-md">
        <span>{meal.calories} kcal</span>
        <span>{meal.protein_g}g protein</span>
        <span>{meal.carbs_g}g carbs</span>
        <span>{meal.fat_g}g fat</span>
      </div>
      <div className="flex gap-sm">
        <Button
          variant={status === 'completed' ? 'primary' : 'secondary'}
          className="h-9 px-md"
          onClick={() => onSetStatus('completed')}
          loading={saving}
        >
          Mark eaten
        </Button>
        <Button
          variant={status === 'skipped' ? 'primary' : 'ghost'}
          className="h-9 px-md"
          onClick={() => onSetStatus('skipped')}
          loading={saving}
        >
          Skip
        </Button>
      </div>
    </div>
  )
}
