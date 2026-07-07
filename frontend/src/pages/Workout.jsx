import { useState, useEffect, useMemo } from 'react'
import AppLayout from '../layouts/AppLayout.jsx'
import Card from '../components/ui/Card.jsx'
import Button from '../components/ui/Button.jsx'
import ExerciseCard from '../components/workout/ExerciseCard.jsx'
import WeekScheduleTabs from '../components/workout/WeekScheduleTabs.jsx'
import WorkoutCalendarView from '../components/workout/WorkoutCalendarView.jsx'
import PlanInfoCard from '../components/shared/PlanInfoCard.jsx'
import WeekNavigator from '../components/shared/WeekNavigator.jsx'
import HistoryList from '../components/shared/HistoryList.jsx'
import * as workoutService from '../services/workoutService'
import { addDays, todayIso, mondayOfWeek, weeksBetween } from '../utils/dateUtils.js'
import { useToast } from '../context/ToastContext.jsx'

export default function Workout() {
  const { showToast } = useToast()
  const [view, setView] = useState('weekly') // 'weekly' | 'calendar'
  const [showHistory, setShowHistory] = useState(false)
  const [offset, setOffset] = useState(0)

  const [weekData, setWeekData] = useState(null)
  const [completions, setCompletions] = useState({})
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(0)
  const [regenerating, setRegenerating] = useState(false)
  const [savingStatus, setSavingStatus] = useState(false)

  const loadWeek = async (weekOffset) => {
    setLoading(true)
    try {
      const [weekResp, completionsData] = await Promise.all([
        workoutService.getWorkoutWeek(weekOffset),
        workoutService.getWorkoutWeekCompletions(weekOffset),
      ])
      setWeekData(weekResp)
      setCompletions(completionsData)

      if (weekOffset === 0 && weekResp.plan) {
        const today = todayIso()
        const todayIndex = weekResp.plan.schedule.findIndex((_, i) => addDays(weekResp.plan.week_start_date, i) === today)
        setSelectedIndex(todayIndex >= 0 ? todayIndex : 0)
      } else {
        setSelectedIndex(0)
      }
    } catch {
      setError('Could not load your workout plan.')
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
      workoutService.getWorkoutHistory().then((data) => setHistory(data.entries))
    }
  }, [showHistory])

  const scheduleWithDates = useMemo(() => {
    if (!weekData?.plan) return []
    return weekData.plan.schedule.map((day, i) => ({ ...day, date: addDays(weekData.plan.week_start_date, i) }))
  }, [weekData])

  const selectedDay = scheduleWithDates[selectedIndex]
  const currentStatus = selectedDay ? completions[selectedDay.date] : null

  const handleRegenerate = async () => {
    setRegenerating(true)
    try {
      const weekResp = await workoutService.regenerateWorkoutWeek(offset)
      setWeekData(weekResp)
      setCompletions({})
      showToast('Workout plan regenerated.', 'success')
    } catch {
      showToast('Could not regenerate your workout plan.', 'error')
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

  const handleSelectHistoryEntry = (weekStartDate) => {
    const targetOffset = weeksBetween(mondayOfWeek(todayIso()), weekStartDate)
    setOffset(targetOffset)
    setShowHistory(false)
    setView('weekly')
  }

  if (error) {
    return (
      <AppLayout title="Workout">
        <p className="text-body-md text-error">{error}</p>
      </AppLayout>
    )
  }

  return (
    <AppLayout title="Workout">
      <div className="flex flex-wrap items-center justify-between gap-md mb-lg">
        <div>
          <h1 className="text-headline-md text-on-surface">Workout</h1>
          <p className="text-body-sm text-on-surface-variant">Plan, track, and review your training.</p>
        </div>
        <div className="flex items-center gap-sm">
          <div className="flex rounded-full bg-surface-container p-xs">
            <button
              className={`h-9 px-md rounded-full text-label-md transition-colors ${view === 'weekly' ? 'bg-primary text-on-primary' : 'text-on-surface-variant'}`}
              onClick={() => setView('weekly')}
            >
              Weekly
            </button>
            <button
              className={`h-9 px-md rounded-full text-label-md transition-colors ${view === 'calendar' ? 'bg-primary text-on-primary' : 'text-on-surface-variant'}`}
              onClick={() => setView('calendar')}
            >
              Calendar
            </button>
          </div>
          <Button variant="ghost" className="h-10 px-md" onClick={() => setShowHistory((s) => !s)}>
            History
          </Button>
        </div>
      </div>

      {showHistory ? (
        <Card className="mb-lg">
          <h2 className="text-headline-sm text-on-surface mb-md">Workout history</h2>
          <HistoryList
            entries={history}
            onSelect={handleSelectHistoryEntry}
            emptyMessage="No past weeks yet — come back after your first full week!"
          />
        </Card>
      ) : null}

      {view === 'calendar' ? (
        <WorkoutCalendarView />
      ) : loading ? (
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
                  ? "No plan existed for this period — this week was before you joined EvoFit."
                  : 'No plan available for this week yet.'}
              </p>
            </Card>
          ) : (
            <>
              <PlanInfoCard planInfo={weekData.plan_info} extraFields={[{ label: 'Workout days', value: weekData.plan_info?.workout_days }]} />

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
            </>
          )}
        </>
      )}
    </AppLayout>
  )
}
