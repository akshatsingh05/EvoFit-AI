import { RefreshCw } from 'lucide-react'
import Button from '../ui/Button.jsx'

const MEAL_LABELS = {
  breakfast: 'Breakfast',
  lunch: 'Lunch',
  snack: 'Snack',
  snack_2: 'Snack',
  snack_3: 'Snack',
  dinner: 'Dinner',
}

export default function MealCard({ meal, status, onSetStatus, saving, onReplace, replacing }) {
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
      <div className="flex items-start justify-between gap-sm mb-xs">
        <h4 className="text-label-lg font-display text-on-surface">{meal.name}</h4>
        {onReplace ? (
          <button
            type="button"
            onClick={() => onReplace(null)}
            disabled={replacing}
            className="shrink-0 flex items-center gap-xs text-body-sm text-primary hover:underline disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ${replacing ? 'animate-spin' : ''}`} />
            Replace
          </button>
        ) : null}
      </div>
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
