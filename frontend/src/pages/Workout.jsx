import { useState, useEffect, useMemo } from 'react'
import AppLayout from '../layouts/AppLayout.jsx'
import Card from '../components/ui/Card.jsx'
import Button from '../components/ui/Button.jsx'
import ExerciseCard from '../components/workout/ExerciseCard.jsx'
import WeekScheduleTabs from '../components/workout/WeekScheduleTabs.jsx'
import * as workoutService from '../services/workoutService'

function addDays(isoDate, days) {
  const d = new Date(isoDate + 'T00:00:00')
  d.setDate(d.getDate() + days)
  return d.toISOString().slice(0, 10)
}

function todayIso() {
  return new Date().toISOString().slice(0, 10)
}

export default function Workout() {
  const [plan, setPlan] = useState(null)
  const [completions, setCompletions] = useState({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(0)
  const [regenerating, setRegenerating] = useState(false)
  const [savingStatus, setSavingStatus] = useState(false)

  const load = async () => {
    try {
      const [planData, completionsData] = await Promise.all([
        workoutService.getWorkoutPlan(),
        workoutService.getWorkoutCompletions(),
      ])
      setPlan(planData)
      setCompletions(completionsData)

      const today = todayIso()
      const todayIndex = planData.schedule.findIndex((_, i) => addDays(planData.week_start_date, i) === today)
      setSelectedIndex(todayIndex >= 0 ? todayIndex : 0)
    } catch {
      setError('Could not load your workout plan.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  const scheduleWithDates = useMemo(() => {
    if (!plan) return []
    return plan.schedule.map((day, i) => ({ ...day, date: addDays(plan.week_start_date, i) }))
  }, [plan])

  const selectedDay = scheduleWithDates[selectedIndex]

  const handleRegenerate = async () => {
    setRegenerating(true)
    try {
      const planData = await workoutService.regenerateWorkoutPlan()
      setPlan(planData)
      setCompletions({})
    } finally {
      setRegenerating(false)
    }
  }

  const handleStatus = async (status) => {
    if (!selectedDay) return
    setSavingStatus(true)
    try {
      await workoutService.saveWorkoutCompletion({ workoutDate: selectedDay.date, status })
      setCompletions((c) => ({ ...c, [selectedDay.date]: status }))
    } finally {
      setSavingStatus(false)
    }
  }

  if (loading) {
    return (
      <AppLayout title="Workout">
        <div className="flex justify-center py-xxl">
          <span className="h-8 w-8 rounded-full border-2 border-primary border-t-transparent animate-spin" />
        </div>
      </AppLayout>
    )
  }

  if (error || !plan) {
    return (
      <AppLayout title="Workout">
        <p className="text-body-md text-error">{error}</p>
      </AppLayout>
    )
  }

  const currentStatus = selectedDay ? completions[selectedDay.date] : null

  return (
    <AppLayout title="Workout">
      <div className="flex items-center justify-between mb-lg">
        <div>
          <h1 className="text-headline-md text-on-surface">This week's plan</h1>
          <p className="text-body-sm text-on-surface-variant">Week of {plan.week_start_date}</p>
        </div>
        <Button variant="ghost" className="h-10 px-md" onClick={handleRegenerate} loading={regenerating}>
          Regenerate plan
        </Button>
      </div>

      <div className="mb-lg">
        <WeekScheduleTabs
          schedule={scheduleWithDates}
          selectedIndex={selectedIndex}
          onSelect={setSelectedIndex}
          completions={completions}
        />
      </div>

      {selectedDay ? (
        <Card>
          <div className="flex items-center justify-between mb-md">
            <div>
              <h2 className="text-headline-sm text-on-surface">{selectedDay.day_name}</h2>
              {!selectedDay.is_rest_day ? (
                <p className="text-body-sm text-on-surface-variant">
                  {selectedDay.focus.replace('_', ' ')} · ~{selectedDay.estimated_duration_minutes} min
                </p>
              ) : null}
            </div>
            {currentStatus ? (
              <span
                className={`text-label-sm px-md h-8 rounded-full flex items-center ${
                  currentStatus === 'completed' ? 'bg-primary/10 text-primary' : 'bg-surface-container-high text-on-surface-variant'
                }`}
              >
                {currentStatus === 'completed' ? 'Completed' : 'Skipped'}
              </span>
            ) : null}
          </div>

          {selectedDay.is_rest_day ? (
            <p className="text-body-md text-on-surface-variant">Rest day — no exercises scheduled.</p>
          ) : (
            <>
              <div>
                {selectedDay.exercises.map((ex, i) => (
                  <ExerciseCard key={ex.name + i} exercise={ex} index={i} />
                ))}
              </div>

              <div className="flex gap-sm mt-lg">
                <Button
                  variant={currentStatus === 'completed' ? 'primary' : 'secondary'}
                  onClick={() => handleStatus('completed')}
                  loading={savingStatus}
                >
                  Mark completed
                </Button>
                <Button
                  variant={currentStatus === 'skipped' ? 'primary' : 'ghost'}
                  onClick={() => handleStatus('skipped')}
                  loading={savingStatus}
                >
                  Skip
                </Button>
              </div>
            </>
          )}
        </Card>
      ) : null}
    </AppLayout>
  )
}
