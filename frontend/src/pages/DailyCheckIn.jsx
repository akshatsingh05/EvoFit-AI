import { useState, useEffect } from 'react'
import { useForm, Controller } from 'react-hook-form'
import { useNavigate } from 'react-router-dom'
import AppLayout from '../layouts/AppLayout.jsx'
import Card from '../components/ui/Card.jsx'
import Input from '../components/ui/Input.jsx'
import Button from '../components/ui/Button.jsx'
import OptionCard from '../components/ui/OptionCard.jsx'
import ScaleSelector from '../components/checkin/ScaleSelector.jsx'
import * as checkinService from '../services/checkinService'
import * as adaptiveService from '../services/adaptiveService'

const MOODS = [
  { value: 'great', label: 'Great' },
  { value: 'good', label: 'Good' },
  { value: 'okay', label: 'Okay' },
  { value: 'low', label: 'Low' },
  { value: 'bad', label: 'Bad' },
]

function todayIso() {
  return new Date().toISOString().slice(0, 10)
}

export default function DailyCheckIn() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [alreadyCheckedIn, setAlreadyCheckedIn] = useState(false)
  const [serverError, setServerError] = useState('')
  const [analyzing, setAnalyzing] = useState(false)
  const [submitted, setSubmitted] = useState(false)

  const {
    register,
    control,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
  } = useForm({
    defaultValues: {
      workout_completed: null,
      workout_difficulty: null,
      sleep_hours: '',
      energy_level: null,
      water_intake_ml: '',
      current_weight_kg: '',
      mood: null,
      muscle_soreness: null,
      pain_level: null,
      notes: '',
    },
  })

  const workoutCompleted = watch('workout_completed')

  useEffect(() => {
    async function load() {
      try {
        const existing = await checkinService.getTodayCheckIn()
        setAlreadyCheckedIn(!!existing)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const onSubmit = async (values) => {
    setServerError('')
    try {
      await checkinService.saveCheckIn({
        checkin_date: todayIso(),
        workout_completed: values.workout_completed,
        workout_difficulty: values.workout_completed ? values.workout_difficulty : null,
        sleep_hours: Number(values.sleep_hours),
        energy_level: values.energy_level,
        water_intake_ml: Number(values.water_intake_ml),
        current_weight_kg: values.current_weight_kg ? Number(values.current_weight_kg) : null,
        mood: values.mood,
        muscle_soreness: values.muscle_soreness,
        pain_level: values.pain_level,
        notes: values.notes || null,
      })
      setSubmitted(true)
      setAnalyzing(true)
      await adaptiveService.generateInsight()
    } catch (err) {
      setServerError(err.response?.data?.detail || 'Could not save your check-in. Please try again.')
    } finally {
      setAnalyzing(false)
    }
  }

  if (loading) {
    return (
      <AppLayout title="Daily Check-In">
        <div className="flex justify-center py-xxl">
          <span className="h-8 w-8 rounded-full border-2 border-primary border-t-transparent animate-spin" />
        </div>
      </AppLayout>
    )
  }

  if (submitted) {
    return (
      <AppLayout title="Daily Check-In">
        <Card>
          {analyzing ? (
            <div className="flex items-center gap-md py-md">
              <span className="h-6 w-6 rounded-full border-2 border-primary border-t-transparent animate-spin" />
              <p className="text-body-md text-on-surface-variant">Updating your recovery score and plans…</p>
            </div>
          ) : (
            <>
              <h2 className="text-headline-sm text-on-surface mb-sm">Check-in saved</h2>
              <p className="text-body-md text-on-surface-variant mb-md">
                Your recovery score and today's plans have been updated based on how you're feeling.
              </p>
              <div className="flex gap-sm">
                <Button onClick={() => navigate('/dashboard')}>Go to dashboard</Button>
                <Button variant="ghost" onClick={() => navigate('/progress')}>View progress</Button>
              </div>
            </>
          )}
        </Card>
      </AppLayout>
    )
  }

  return (
    <AppLayout title="Daily Check-In">
      {alreadyCheckedIn ? (
        <Card className="mb-lg bg-primary-container/10">
          <p className="text-body-sm text-on-surface">
            You've already checked in today. Submitting again will update today's entry.
          </p>
        </Card>
      ) : null}

      <form onSubmit={handleSubmit(onSubmit)}>
        <Card className="mb-lg">
          <h2 className="text-headline-sm text-on-surface mb-md">Today's workout</h2>
          <div className="grid grid-cols-2 gap-sm mb-md">
            <Controller
              name="workout_completed"
              control={control}
              rules={{ validate: (v) => v !== null || 'Please select an option' }}
              render={({ field }) => (
                <>
                  <OptionCard label="Completed it" selected={field.value === true} onSelect={() => field.onChange(true)} />
                  <OptionCard label="Didn't work out" selected={field.value === false} onSelect={() => field.onChange(false)} />
                </>
              )}
            />
          </div>
          {errors.workout_completed ? <p className="text-body-sm text-error mb-md">{errors.workout_completed.message}</p> : null}

          {workoutCompleted ? (
            <Controller
              name="workout_difficulty"
              control={control}
              rules={{ required: 'Please rate the difficulty' }}
              render={({ field }) => (
                <ScaleSelector
                  label="How difficult was it?"
                  value={field.value}
                  onChange={field.onChange}
                  lowLabel="Very easy"
                  highLabel="Max effort"
                />
              )}
            />
          ) : null}
        </Card>

        <Card className="mb-lg">
          <h2 className="text-headline-sm text-on-surface mb-md">Recovery</h2>
          <div className="grid grid-cols-2 gap-md mb-md">
            <Input
              label="Sleep hours"
              type="number"
              step="0.5"
              error={errors.sleep_hours?.message}
              {...register('sleep_hours', { required: 'Required', min: { value: 0, message: 'Invalid' }, max: { value: 24, message: 'Invalid' } })}
            />
            <Input
              label="Water intake (ml)"
              type="number"
              error={errors.water_intake_ml?.message}
              {...register('water_intake_ml', { required: 'Required', min: { value: 0, message: 'Invalid' } })}
            />
          </div>

          <div className="mb-md">
            <Controller
              name="energy_level"
              control={control}
              rules={{ required: 'Please rate your energy' }}
              render={({ field }) => (
                <ScaleSelector label="Energy level" value={field.value} onChange={field.onChange} lowLabel="Drained" highLabel="Energized" />
              )}
            />
            {errors.energy_level ? <p className="text-body-sm text-error mt-xs">{errors.energy_level.message}</p> : null}
          </div>

          <div className="mb-md">
            <Controller
              name="muscle_soreness"
              control={control}
              rules={{ required: 'Please rate your soreness' }}
              render={({ field }) => (
                <ScaleSelector label="Muscle soreness" value={field.value} onChange={field.onChange} lowLabel="None" highLabel="Very sore" />
              )}
            />
            {errors.muscle_soreness ? <p className="text-body-sm text-error mt-xs">{errors.muscle_soreness.message}</p> : null}
          </div>

          <div>
            <Controller
              name="pain_level"
              control={control}
              rules={{ required: 'Please rate your pain level' }}
              render={({ field }) => (
                <ScaleSelector label="Pain level" value={field.value} onChange={field.onChange} min={0} max={5} lowLabel="None" highLabel="Severe" />
              )}
            />
            {errors.pain_level ? <p className="text-body-sm text-error mt-xs">{errors.pain_level.message}</p> : null}
          </div>
        </Card>

        <Card className="mb-lg">
          <h2 className="text-headline-sm text-on-surface mb-md">Mood & weight</h2>
          <div className="mb-md">
            <span className="block mb-sm text-label-md text-on-surface-variant">Mood</span>
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-sm">
              <Controller
                name="mood"
                control={control}
                rules={{ required: true }}
                render={({ field }) => (
                  <>
                    {MOODS.map((m) => (
                      <OptionCard key={m.value} label={m.label} selected={field.value === m.value} onSelect={() => field.onChange(m.value)} />
                    ))}
                  </>
                )}
              />
            </div>
            {errors.mood ? <p className="text-body-sm text-error mt-xs">Please select your mood</p> : null}
          </div>

          <Input label="Current weight (kg, optional)" type="number" step="0.1" {...register('current_weight_kg')} />
        </Card>

        <Card className="mb-lg">
          <h2 className="text-headline-sm text-on-surface mb-md">Notes (optional)</h2>
          <textarea
            className="w-full min-h-[80px] p-md bg-input-fill rounded-md text-body-md focus:outline-none focus:ring-2 focus:ring-primary"
            placeholder="Anything else worth noting today?"
            {...register('notes')}
          />
        </Card>

        {serverError ? <p className="text-body-sm text-error mb-md">{serverError}</p> : null}

        <Button type="submit" loading={isSubmitting}>Save check-in</Button>
      </form>
    </AppLayout>
  )
}
