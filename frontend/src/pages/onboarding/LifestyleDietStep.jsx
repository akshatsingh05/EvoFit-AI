import { useForm, Controller } from 'react-hook-form'
import OnboardingLayout from '../../layouts/OnboardingLayout.jsx'
import Input from '../../components/ui/Input.jsx'
import OptionCard from '../../components/ui/OptionCard.jsx'

const DIET_TYPES = [
  { value: 'omnivore', label: 'Omnivore' },
  { value: 'vegetarian', label: 'Vegetarian' },
  { value: 'vegan', label: 'Vegan' },
  { value: 'pescatarian', label: 'Pescatarian' },
  { value: 'keto', label: 'Keto' },
  { value: 'other', label: 'Other' },
]

const STRESS_LEVELS = [
  { value: 'low', label: 'Low' },
  { value: 'moderate', label: 'Moderate' },
  { value: 'high', label: 'High' },
]

const ACTIVITY_LEVELS = [
  { value: 'sedentary', label: 'Sedentary', description: 'Desk job, little walking' },
  { value: 'light', label: 'Light', description: 'On your feet occasionally' },
  { value: 'active', label: 'Active', description: 'On your feet most of the day' },
  { value: 'very_active', label: 'Very active', description: 'Physically demanding work' },
]

export default function LifestyleDietStep({ defaultValues, onBack, onNext, stepIndex, stepCount, saving }) {
  const {
    register,
    control,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm({
    mode: 'onChange',
    defaultValues: {
      diet_type: defaultValues?.diet_type || '',
      meals_per_day: defaultValues?.meals_per_day || 3,
      sleep_hours_avg: defaultValues?.sleep_hours_avg || 7,
      stress_level: defaultValues?.stress_level || '',
      occupation_activity: defaultValues?.occupation_activity || '',
    },
  })

  const dietType = watch('diet_type')
  const stressLevel = watch('stress_level')
  const activity = watch('occupation_activity')

  const submit = (values) =>
    onNext({
      ...values,
      meals_per_day: Number(values.meals_per_day),
      sleep_hours_avg: Number(values.sleep_hours_avg),
    })

  return (
    <OnboardingLayout
      stepIndex={stepIndex}
      stepCount={stepCount}
      stepLabel={`Step ${stepIndex} of ${stepCount} — Lifestyle & diet`}
      title="How do you eat and live day-to-day?"
      subtitle="This tunes your nutrition plan and recovery expectations."
      onBack={onBack}
      onNext={handleSubmit(submit)}
      nextDisabled={!dietType || !stressLevel || !activity}
      nextLoading={saving}
    >
      <div className="space-y-lg">
        <div>
          <span className="block mb-sm text-label-md text-on-surface-variant">Diet type</span>
          <div className="grid grid-cols-2 gap-sm">
            {DIET_TYPES.map((opt) => (
              <Controller
                key={opt.value}
                name="diet_type"
                control={control}
                rules={{ required: true }}
                render={({ field }) => (
                  <OptionCard label={opt.label} selected={field.value === opt.value} onSelect={() => field.onChange(opt.value)} />
                )}
              />
            ))}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-md">
          <Input
            label="Meals per day"
            type="number"
            error={errors.meals_per_day?.message}
            {...register('meals_per_day', { required: true, min: 1, max: 8 })}
          />
          <Input
            label="Average sleep (hours)"
            type="number"
            step="0.5"
            error={errors.sleep_hours_avg?.message}
            {...register('sleep_hours_avg', { required: true, min: 0, max: 24 })}
          />
        </div>

        <div>
          <span className="block mb-sm text-label-md text-on-surface-variant">Stress level</span>
          <div className="grid grid-cols-3 gap-sm">
            {STRESS_LEVELS.map((opt) => (
              <Controller
                key={opt.value}
                name="stress_level"
                control={control}
                rules={{ required: true }}
                render={({ field }) => (
                  <OptionCard label={opt.label} selected={field.value === opt.value} onSelect={() => field.onChange(opt.value)} />
                )}
              />
            ))}
          </div>
        </div>

        <div>
          <span className="block mb-sm text-label-md text-on-surface-variant">Daily activity outside workouts</span>
          <div className="grid gap-sm">
            {ACTIVITY_LEVELS.map((opt) => (
              <Controller
                key={opt.value}
                name="occupation_activity"
                control={control}
                rules={{ required: true }}
                render={({ field }) => (
                  <OptionCard
                    label={opt.label}
                    description={opt.description}
                    selected={field.value === opt.value}
                    onSelect={() => field.onChange(opt.value)}
                  />
                )}
              />
            ))}
          </div>
        </div>
      </div>
    </OnboardingLayout>
  )
}
