import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { Link } from 'react-router-dom'
import AppLayout from '../layouts/AppLayout.jsx'
import Card from '../components/ui/Card.jsx'
import Input from '../components/ui/Input.jsx'
import Button from '../components/ui/Button.jsx'
import ProgressChart from '../components/progress/ProgressChart.jsx'
import * as progressService from '../services/progressService'
import * as reportsService from '../services/reportsService'
import { getErrorMessage } from '../utils/errorMessage.js'

function todayIso() {
  return new Date().toISOString().slice(0, 10)
}

function formatDayLabel(isoDate) {
  const d = new Date(isoDate + 'T00:00:00')
  return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}

function formatDateTimeLabel(isoDateTime) {
  const d = new Date(isoDateTime)
  return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}

export default function Progress() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [logError, setLogError] = useState('')
  const [reportPeriod, setReportPeriod] = useState('weekly')
  const [report, setReport] = useState(null)
  const [reportLoading, setReportLoading] = useState(true)

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm({ defaultValues: { weight_kg: '' } })

  const load = async () => {
    try {
      const result = await progressService.getProgress()
      setData(result)
    } catch {
      setError('Could not load your progress.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  useEffect(() => {
    let cancelled = false
    setReportLoading(true)
    reportsService
      .getReport(reportPeriod)
      .then((result) => {
        if (!cancelled) setReport(result)
      })
      .finally(() => {
        if (!cancelled) setReportLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [reportPeriod])

  const onLogWeight = async (values) => {
    setLogError('')
    try {
      await progressService.logWeight({ logDate: todayIso(), weightKg: Number(values.weight_kg) })
      reset({ weight_kg: '' })
      await load()
    } catch (err) {
      setLogError(getErrorMessage(err, 'Could not save that weight entry.'))
    }
  }

  if (loading) {
    return (
      <AppLayout title="Progress">
        <div className="flex justify-center py-xxl">
          <span className="h-8 w-8 rounded-full border-2 border-primary border-t-transparent animate-spin" />
        </div>
      </AppLayout>
    )
  }

  if (error || !data) {
    return (
      <AppLayout title="Progress">
        <p className="text-body-md text-error">{error}</p>
      </AppLayout>
    )
  }

  const weightPoints = data.weight_history.map((w) => ({ label: formatDayLabel(w.log_date), value: w.weight_kg }))
  const recoveryPoints = data.recovery_history.map((r) => ({
    label: formatDateTimeLabel(r.created_at),
    value: r.recovery_score,
  }))

  const completedWorkouts = data.workout_history.filter((w) => w.status === 'completed').length
  const skippedWorkouts = data.workout_history.filter((w) => w.status === 'skipped').length

  return (
    <AppLayout title="Progress">
      <div className="space-y-lg">
        <div className="grid sm:grid-cols-3 gap-lg">
          <Card>
            <h3 className="text-label-lg font-display text-on-surface mb-sm">Workout streak</h3>
            <p className="text-headline-md text-tertiary">{data.workout_streak_days} <span className="text-body-md text-on-surface-variant">days</span></p>
          </Card>
          <Card>
            <h3 className="text-label-lg font-display text-on-surface mb-sm">Fitness score</h3>
            <p className="text-headline-md text-secondary">{data.fitness_score}<span className="text-body-md text-on-surface-variant">/100</span></p>
          </Card>
          <Card>
            <h3 className="text-label-lg font-display text-on-surface mb-sm">Recovery trend</h3>
            {data.recovery_trend === null ? (
              <>
                <p className="text-headline-md text-on-surface-variant">—</p>
                <p className="text-body-sm text-on-surface-variant mt-xs">
                  <Link to="/checkin" className="text-secondary">Check in</Link> to start tracking recovery.
                </p>
              </>
            ) : (
              <p className="text-headline-md text-primary">{data.recovery_trend[data.recovery_trend.length - 1]}</p>
            )}
          </Card>
        </div>

        <div className="grid sm:grid-cols-2 gap-lg">
          <Card>
            <h3 className="text-label-lg font-display text-on-surface mb-sm">Workout consistency</h3>
            <p className="text-headline-md text-primary">{data.workout_consistency_pct}<span className="text-body-md text-on-surface-variant">%</span></p>
            <p className="text-body-sm text-on-surface-variant mt-xs">Completed vs. logged over the last 14 days</p>
          </Card>
          <Card>
            <h3 className="text-label-lg font-display text-on-surface mb-sm">Nutrition consistency</h3>
            <p className="text-headline-md text-secondary">{data.nutrition_consistency_pct}<span className="text-body-md text-on-surface-variant">%</span></p>
            <p className="text-body-sm text-on-surface-variant mt-xs">Meals marked eaten over the last 14 days</p>
          </Card>
        </div>

        <Card>
          <div className="flex items-center justify-between mb-md">
            <h3 className="text-label-lg font-display text-on-surface">Reports</h3>
            <div className="flex rounded-full bg-surface-container p-xs" role="group" aria-label="Report period">
              <button
                className={`h-8 px-md rounded-full text-label-sm transition-colors ${reportPeriod === 'weekly' ? 'bg-primary text-on-primary' : 'text-on-surface-variant'}`}
                aria-pressed={reportPeriod === 'weekly'}
                onClick={() => setReportPeriod('weekly')}
              >
                Weekly
              </button>
              <button
                className={`h-8 px-md rounded-full text-label-sm transition-colors ${reportPeriod === 'monthly' ? 'bg-primary text-on-primary' : 'text-on-surface-variant'}`}
                aria-pressed={reportPeriod === 'monthly'}
                onClick={() => setReportPeriod('monthly')}
              >
                Monthly
              </button>
            </div>
          </div>

          {reportLoading || !report ? (
            <div className="flex justify-center py-lg">
              <span className="h-6 w-6 rounded-full border-2 border-primary border-t-transparent animate-spin" aria-hidden="true" />
            </div>
          ) : (
            <>
              <p className="text-body-md text-on-surface mb-md">{report.ai_summary}</p>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-md">
                <div>
                  <p className="text-body-sm text-on-surface-variant">Workouts done</p>
                  <p className="text-headline-sm text-primary">{report.workouts_completed}</p>
                </div>
                <div>
                  <p className="text-body-sm text-on-surface-variant">Frequency</p>
                  <p className="text-headline-sm text-secondary">{report.workout_frequency_pct}%</p>
                </div>
                <div>
                  <p className="text-body-sm text-on-surface-variant">Calories logged</p>
                  <p className="text-headline-sm text-tertiary">{report.total_calories_logged}</p>
                </div>
                <div>
                  <p className="text-body-sm text-on-surface-variant">Weight change</p>
                  <p className="text-headline-sm text-on-surface">
                    {report.weight_change_kg === null ? '—' : `${report.weight_change_kg > 0 ? '+' : ''}${report.weight_change_kg} kg`}
                  </p>
                </div>
              </div>
            </>
          )}
        </Card>

        <ProgressChart
          title="Weight history"
          points={weightPoints}
          unit=" kg"
          emptyMessage="Log your weight below to start tracking a trend."
        />

        <ProgressChart
          title="Recovery history"
          points={recoveryPoints}
          unit="/100"
          emptyMessage="Complete a daily check-in to start tracking your recovery score."
        />

        <Card>
          <h3 className="text-label-lg font-display text-on-surface mb-md">Log today's weight</h3>
          <form onSubmit={handleSubmit(onLogWeight)} className="flex items-end gap-md max-w-[320px]">
            <div className="flex-1">
              <Input
                label="Weight (kg)"
                type="number"
                step="0.1"
                error={errors.weight_kg?.message}
                {...register('weight_kg', { required: 'Required', min: { value: 1, message: 'Invalid' } })}
              />
            </div>
            <Button type="submit" loading={isSubmitting} className="h-[56px]">Log</Button>
          </form>
          {logError ? <p className="text-body-sm text-error mt-sm">{logError}</p> : null}
        </Card>

        <div className="grid sm:grid-cols-2 gap-lg">
          <Card>
            <h3 className="text-label-lg font-display text-on-surface mb-sm">Workout completion history</h3>
            <div className="flex gap-lg mb-md">
              <div>
                <p className="text-headline-sm text-primary">{completedWorkouts}</p>
                <p className="text-body-sm text-on-surface-variant">Completed</p>
              </div>
              <div>
                <p className="text-headline-sm text-on-surface-variant">{skippedWorkouts}</p>
                <p className="text-body-sm text-on-surface-variant">Skipped</p>
              </div>
            </div>
            {data.workout_history.length === 0 ? (
              <p className="text-body-sm text-on-surface-variant">No workouts logged yet.</p>
            ) : (
              <ul className="text-body-sm text-on-surface-variant space-y-xs">
                {data.workout_history.slice(-7).reverse().map((w) => (
                  <li key={w.workout_date} className="flex justify-between">
                    <span>{formatDayLabel(w.workout_date)}</span>
                    <span className={w.status === 'completed' ? 'text-primary' : 'text-on-surface-variant'}>
                      {w.status}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </Card>

          <Card>
            <h3 className="text-label-lg font-display text-on-surface mb-sm">Nutrition adherence</h3>
            <div className="flex gap-lg mb-md">
              <div>
                <p className="text-headline-sm text-primary">{data.total_calories_logged_today}</p>
                <p className="text-body-sm text-on-surface-variant">Calories today</p>
              </div>
              <div>
                <p className="text-headline-sm text-secondary">{data.total_protein_logged_today}g</p>
                <p className="text-body-sm text-on-surface-variant">Protein today</p>
              </div>
            </div>
            {data.nutrition_adherence.length === 0 ? (
              <p className="text-body-sm text-on-surface-variant">No meals logged yet.</p>
            ) : (
              <ul className="text-body-sm text-on-surface-variant space-y-xs">
                {data.nutrition_adherence.slice(-7).reverse().map((n) => (
                  <li key={n.meal_date} className="flex justify-between">
                    <span>{formatDayLabel(n.meal_date)}</span>
                    <span>{n.completed_count}/{n.total_count} meals logged</span>
                  </li>
                ))}
              </ul>
            )}
          </Card>
        </div>

        <Card>
          <h3 className="text-label-lg font-display text-on-surface mb-sm">Daily check-in history</h3>
          {data.checkin_history.length === 0 ? (
            <p className="text-body-sm text-on-surface-variant">
              No check-ins yet. <Link to="/checkin" className="text-secondary">Do your first check-in.</Link>
            </p>
          ) : (
            <ul className="text-body-sm text-on-surface-variant space-y-sm">
              {data.checkin_history.slice(0, 7).map((c) => (
                <li key={c.checkin_date} className="flex flex-wrap gap-x-md gap-y-xs justify-between border-b border-divider last:border-none pb-sm last:pb-0">
                  <span className="font-medium text-on-surface">{formatDayLabel(c.checkin_date)}</span>
                  <span className="capitalize">{c.mood}</span>
                  <span>{c.sleep_hours}h sleep</span>
                  <span>Energy {c.energy_level}/5</span>
                  <span>Pain {c.pain_level}/5</span>
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card>
          <h3 className="text-label-lg font-display text-on-surface mb-sm">AI recommendation history</h3>
          {data.ai_recommendation_history.length === 0 ? (
            <p className="text-body-sm text-on-surface-variant">No recommendations generated yet.</p>
          ) : (
            <div className="space-y-md">
              {data.ai_recommendation_history.slice(0, 5).map((entry) => (
                <div key={entry.created_at} className="border-b border-divider last:border-none pb-md last:pb-0">
                  <p className="text-label-sm text-on-surface-variant mb-xs">{formatDateTimeLabel(entry.created_at)}</p>
                  <ul className="space-y-xs">
                    {entry.recommendations.map((rec, i) => (
                      <li key={i} className="text-body-sm text-on-surface">• {rec}</li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>
    </AppLayout>
  )
}
