import { useForm, Controller } from 'react-hook-form'
import OnboardingLayout from '../../layouts/OnboardingLayout.jsx'
import Input from '../../components/ui/Input.jsx'
import OptionCard from '../../components/ui/OptionCard.jsx'
import MultiChipToggle from '../../components/ui/MultiChipToggle.jsx'

const EXPERIENCE_LEVELS = [
  { value: 'beginner', label: 'Beginner', description: 'New to structured training' },
  { value: 'intermediate', label: 'Intermediate', description: 'Training consistently for 6+ months' },
  { value: 'advanced', label: 'Advanced', description: 'Training consistently for 2+ years' },
]

const EQUIPMENT_OPTIONS = [
  { value: 'none', label: 'No equipment', description: 'Bodyweight only' },
  { value: 'home_basic', label: 'Home basics', description: 'Dumbbells, bands, a bench' },
  { value: 'full_gym', label: 'Full gym', description: 'Machines, barbells, full rack' },
]

const WORKOUT_TYPES = [
  { value: 'strength', label: 'Strength' },
  { value: 'cardio', label: 'Cardio' },
  { value: 'hiit', label: 'HIIT' },
  { value: 'yoga', label: 'Yoga / mobility' },
  { value: 'sports', label: 'Sports' },
]

export default function FitnessExperienceStep({ defaultValues, onBack, onNext, stepIndex, stepCount, saving }) {
  const {
    register,
    control,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isValid },
  } = useForm({
    mode: 'onChange',
    defaultValues: {
      experience_level: defaultValues?.experience_level || '',
      workouts_per_week_current: defaultValues?.workouts_per_week_current ?? 0,
      preferred_workout_types: defaultValues?.preferred_workout_types || [],
      equipment_access: defaultValues?.equipment_access || '',
    },
  })

  const experienceLevel = watch('experience_level')
  const equipmentAccess = watch('equipment_access')
  const preferredTypes = watch('preferred_workout_types')

  const toggleType = (value) => {
    const current = preferredTypes || []
    setValue(
      'preferred_workout_types',
      current.includes(value) ? current.filter((v) => v !== value) : [...current, value],
      { shouldValidate: true }
    )
  }

  const submit = (values) =>
    onNext({ ...values, workouts_per_week_current: Number(values.workouts_per_week_current) })

  return (
    <OnboardingLayout
      stepIndex={stepIndex}
      stepCount={stepCount}
      stepLabel={`Step ${stepIndex} of ${stepCount} — Fitness experience`}
      title="What's your training background?"
      subtitle="This sets your starting intensity and exercise complexity."
      onBack={onBack}
      onNext={handleSubmit(submit)}
      nextDisabled={!experienceLevel || !equipmentAccess}
      nextLoading={saving}
    >
      <div className="space-y-lg">
        <div>
          <span className="block mb-sm text-label-md text-on-surface-variant">Experience level</span>
          <div className="grid gap-sm">
            {EXPERIENCE_LEVELS.map((opt) => (
              <Controller
                key={opt.value}
                name="experience_level"
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

        <Input
          label="Workouts per week right now"
          type="number"
          error={errors.workouts_per_week_current?.message}
          {...register('workouts_per_week_current', { required: true, min: 0, max: 14 })}
        />

        <div>
          <span className="block mb-sm text-label-md text-on-surface-variant">Equipment access</span>
          <div className="grid gap-sm">
            {EQUIPMENT_OPTIONS.map((opt) => (
              <Controller
                key={opt.value}
                name="equipment_access"
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

        <div>
          <span className="block mb-sm text-label-md text-on-surface-variant">Preferred workout types (optional)</span>
          <MultiChipToggle options={WORKOUT_TYPES} selected={preferredTypes || []} onToggle={toggleType} />
        </div>
      </div>
    </OnboardingLayout>
  )
}
