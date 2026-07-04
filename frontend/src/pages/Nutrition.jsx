import { useState, useEffect } from 'react'
import AppLayout from '../layouts/AppLayout.jsx'
import Card from '../components/ui/Card.jsx'
import Button from '../components/ui/Button.jsx'
import MealCard from '../components/nutrition/MealCard.jsx'
import * as nutritionService from '../services/nutritionService'

function todayIso() {
  return new Date().toISOString().slice(0, 10)
}

export default function Nutrition() {
  const [plan, setPlan] = useState(null)
  const [completions, setCompletions] = useState({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [regenerating, setRegenerating] = useState(false)
  const [savingMeal, setSavingMeal] = useState(null)

  const load = async () => {
    try {
      const [planData, completionsData] = await Promise.all([
        nutritionService.getNutritionPlan(),
        nutritionService.getMealCompletions(),
      ])
      setPlan(planData)
      setCompletions(completionsData)
    } catch {
      setError('Could not load your nutrition plan.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  const handleRegenerate = async () => {
    setRegenerating(true)
    try {
      const planData = await nutritionService.regenerateNutritionPlan()
      setPlan(planData)
      setCompletions({})
    } finally {
      setRegenerating(false)
    }
  }

  const handleSetStatus = async (mealType, status) => {
    setSavingMeal(mealType)
    try {
      await nutritionService.saveMealCompletion({ mealDate: todayIso(), mealType, status })
      setCompletions((c) => ({ ...c, [mealType]: status }))
    } finally {
      setSavingMeal(null)
    }
  }

  if (loading) {
    return (
      <AppLayout title="Nutrition">
        <div className="flex justify-center py-xxl">
          <span className="h-8 w-8 rounded-full border-2 border-primary border-t-transparent animate-spin" />
        </div>
      </AppLayout>
    )
  }

  if (error || !plan) {
    return (
      <AppLayout title="Nutrition">
        <p className="text-body-md text-error">{error}</p>
      </AppLayout>
    )
  }

  const loggedCalories = plan.meals
    .filter((m) => completions[m.meal_type] === 'completed')
    .reduce((sum, m) => sum + m.calories, 0)

  return (
    <AppLayout title="Nutrition">
      <div className="flex items-center justify-between mb-lg">
        <h1 className="text-headline-md text-on-surface">Today's nutrition</h1>
        <Button variant="ghost" className="h-10 px-md" onClick={handleRegenerate} loading={regenerating}>
          Regenerate plan
        </Button>
      </div>

      <div className="grid sm:grid-cols-2 gap-lg mb-lg">
        <Card>
          <h3 className="text-label-lg font-display text-on-surface mb-sm">Daily targets</h3>
          <p className="text-headline-sm text-primary mb-xs">
            {loggedCalories} <span className="text-body-md text-on-surface-variant">/ {plan.target_calories} kcal</span>
          </p>
          <div className="flex gap-md text-body-sm text-on-surface-variant">
            <span>{plan.target_protein_g}g protein</span>
            <span>{plan.target_carbs_g}g carbs</span>
            <span>{plan.target_fat_g}g fat</span>
          </div>
        </Card>
        <Card>
          <h3 className="text-label-lg font-display text-on-surface mb-sm">Water goal</h3>
          <p className="text-headline-sm text-secondary">
            {(plan.water_goal_ml / 1000).toFixed(1)} <span className="text-body-md text-on-surface-variant">liters</span>
          </p>
        </Card>
      </div>

      <Card>
        {plan.meals.map((meal) => (
          <MealCard
            key={meal.meal_type}
            meal={meal}
            status={completions[meal.meal_type]}
            saving={savingMeal === meal.meal_type}
            onSetStatus={(status) => handleSetStatus(meal.meal_type, status)}
          />
        ))}
      </Card>
    </AppLayout>
  )
}
