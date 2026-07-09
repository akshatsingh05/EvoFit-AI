import { useState, useEffect, useMemo } from 'react'
import AppLayout from '../layouts/AppLayout.jsx'
import Card from '../components/ui/Card.jsx'
import Button from '../components/ui/Button.jsx'
import MealCard from '../components/nutrition/MealCard.jsx'
import WeekScheduleTabs from '../components/workout/WeekScheduleTabs.jsx'
import PlanInfoCard from '../components/shared/PlanInfoCard.jsx'
import WeekNavigator from '../components/shared/WeekNavigator.jsx'
import HistoryList from '../components/shared/HistoryList.jsx'
import * as nutritionService from '../services/nutritionService'
import { replaceMeal } from '../services/nutritionPreferencesService'
import { todayIso, mondayOfWeek, weeksBetween } from '../utils/dateUtils.js'
import { useToast } from '../context/ToastContext.jsx'

function deriveDayDotStatus(mealStatuses) {
  if (!mealStatuses) return undefined
  const values = Object.values(mealStatuses)
  if (values.length === 0) return undefined
  if (values.some((v) => v === 'completed')) return 'completed'
  if (values.every((v) => v === 'skipped')) return 'skipped'
  return undefined
}

export default function Nutrition() {
  const { showToast } = useToast()
  const [showHistory, setShowHistory] = useState(false)
  const [offset, setOffset] = useState(0)

  const [weekData, setWeekData] = useState(null)
  const [completions, setCompletions] = useState({}) // { [date]: { [mealType]: status } }
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(0)
  const [regenerating, setRegenerating] = useState(false)
  const [savingMeal, setSavingMeal] = useState(null)
  const [replacingMealType, setReplacingMealType] = useState(null)

  const loadWeek = async (weekOffset) => {
    setLoading(true)
    try {
      const [weekResp, completionsData] = await Promise.all([
        nutritionService.getNutritionWeek(weekOffset),
        nutritionService.getNutritionWeekCompletions(weekOffset),
      ])
      setWeekData(weekResp)
      setCompletions(completionsData)

      if (weekOffset === 0 && weekResp.plan) {
        const today = todayIso()
        const todayIndex = weekResp.plan.days.findIndex((d) => d.date === today)
        setSelectedIndex(todayIndex >= 0 ? todayIndex : 0)
      } else {
        setSelectedIndex(0)
      }
    } catch {
      setError('Could not load your nutrition plan.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadWeek(offset)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [offset])

  useEffect(() => {
    if (showHistory) {
      nutritionService.getNutritionHistory().then((data) => setHistory(data.entries))
    }
  }, [showHistory])

  const dayDotStatuses = useMemo(() => {
    const map = {}
    for (const [date, meals] of Object.entries(completions)) {
      map[date] = deriveDayDotStatus(meals)
    }
    return map
  }, [completions])

  const days = weekData?.plan?.days || []
  const selectedDay = days[selectedIndex]
  const selectedDayCompletions = selectedDay ? completions[selectedDay.date] || {} : {}

  const handleRegenerate = async () => {
    setRegenerating(true)
    try {
      const weekResp = await nutritionService.regenerateNutritionWeek(offset)
      setWeekData(weekResp)
      setCompletions({})
      showToast('Nutrition plan regenerated.', 'success')
    } catch {
      showToast('Could not regenerate your nutrition plan.', 'error')
    } finally {
      setRegenerating(false)
    }
  }

  const handleSetStatus = async (mealType, status) => {
    if (!selectedDay) return
    setSavingMeal(mealType)
    try {
      await nutritionService.saveMealCompletion({ mealDate: selectedDay.date, mealType, status })
      setCompletions((c) => ({
        ...c,
        [selectedDay.date]: { ...(c[selectedDay.date] || {}), [mealType]: status },
      }))
    } finally {
      setSavingMeal(null)
    }
  }

  const handleSelectHistoryEntry = (weekStartDate) => {
    const targetOffset = weeksBetween(mondayOfWeek(todayIso()), weekStartDate)
    setOffset(targetOffset)
    setShowHistory(false)
  }

  const handleReplaceMeal = async (mealType, replacementName) => {
    setReplacingMealType(mealType)
    try {
      const weekResp = await replaceMeal({
        offset,
        dayIndex: selectedIndex,
        mealType,
        replacementName,
      })
      setWeekData(weekResp)
      showToast('Meal replaced.', 'success')
    } catch {
      showToast('Could not replace that meal. Try a different one.', 'error')
    } finally {
      setReplacingMealType(null)
    }
  }

  if (error) {
    return (
      <AppLayout title="Nutrition">
        <p className="text-body-md text-error">{error}</p>
      </AppLayout>
    )
  }

  const loggedCalories = selectedDay
    ? selectedDay.meals
        .filter((m) => selectedDayCompletions[m.meal_type] === 'completed')
        .reduce((sum, m) => sum + m.calories, 0)
    : 0

  return (
    <AppLayout title="Nutrition">
      <div className="flex flex-wrap items-center justify-between gap-md mb-lg">
        <div>
          <h1 className="text-headline-md text-on-surface">Nutrition</h1>
          <p className="text-body-sm text-on-surface-variant">Plan, log, and review your meals.</p>
        </div>
        <Button variant="ghost" className="h-10 px-md" onClick={() => setShowHistory((s) => !s)}>
          History
        </Button>
      </div>

      {showHistory ? (
        <Card className="mb-lg">
          <h2 className="text-headline-sm text-on-surface mb-md">Nutrition history</h2>
          <HistoryList
            entries={history}
            onSelect={handleSelectHistoryEntry}
            emptyMessage="No past weeks yet — come back after your first full week!"
          />
        </Card>
      ) : null}

      {loading ? (
        <div className="flex justify-center py-xxl">
          <span className="h-8 w-8 rounded-full border-2 border-primary border-t-transparent animate-spin" />
        </div>
      ) : (
        <>
          <div className="flex flex-wrap items-center justify-between gap-md mb-md">
            <WeekNavigator weekStartDate={weekData.week_start_date} offset={offset} onOffsetChange={setOffset} />
            {weekData.plan ? (
              <Button variant="ghost" className="h-10 px-md" onClick={handleRegenerate} loading={regenerating}>
                Regenerate plan
              </Button>
            ) : null}
          </div>

          {!weekData.plan ? (
            <Card>
              <p className="text-body-md text-on-surface-variant">
                {weekData.is_before_registration
                  ? 'No plan existed for this period — this week was before you joined EvoFit.'
                  : 'No plan available for this week yet.'}
              </p>
            </Card>
          ) : (
            <>
              <PlanInfoCard
                planInfo={weekData.plan_info}
                extraFields={[{ label: 'Calories target', value: weekData.plan_info?.calories_target }]}
              />

              <div className="mb-lg">
                <WeekScheduleTabs
                  schedule={days}
                  selectedIndex={selectedIndex}
                  onSelect={setSelectedIndex}
                  completions={dayDotStatuses}
                />
              </div>

              {selectedDay ? (
                <>
                  <div className="grid sm:grid-cols-2 gap-lg mb-lg">
                    <Card>
                      <h3 className="text-label-lg font-display text-on-surface mb-sm">Daily targets</h3>
                      <p className="text-headline-sm text-primary mb-xs">
                        {loggedCalories}{' '}
                        <span className="text-body-md text-on-surface-variant">/ {selectedDay.target_calories} kcal</span>
                      </p>
                      <div className="flex gap-md text-body-sm text-on-surface-variant">
                        <span>{selectedDay.target_protein_g}g protein</span>
                        <span>{selectedDay.target_carbs_g}g carbs</span>
                        <span>{selectedDay.target_fat_g}g fat</span>
                      </div>
                    </Card>
                    <Card>
                      <h3 className="text-label-lg font-display text-on-surface mb-sm">Water goal</h3>
                      <p className="text-headline-sm text-secondary">
                        {(selectedDay.water_goal_ml / 1000).toFixed(1)}{' '}
                        <span className="text-body-md text-on-surface-variant">liters</span>
                      </p>
                    </Card>
                  </div>

                  <Card>
                    {selectedDay.meals.map((meal) => (
                      <MealCard
                        key={meal.meal_type}
                        meal={meal}
                        status={selectedDayCompletions[meal.meal_type]}
                        saving={savingMeal === meal.meal_type}
                        onSetStatus={(status) => handleSetStatus(meal.meal_type, status)}
                        onReplace={(replacementName) => handleReplaceMeal(meal.meal_type, replacementName)}
                        replacing={replacingMealType === meal.meal_type}
                      />
                    ))}
                  </Card>
                </>
              ) : null}
            </>
          )}
        </>
      )}
    </AppLayout>
  )
}
