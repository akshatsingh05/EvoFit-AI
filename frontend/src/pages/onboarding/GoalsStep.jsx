import { useForm, Controller } from 'react-hook-form'
import OnboardingLayout from '../../layouts/OnboardingLayout.jsx'
import Input from '../../components/ui/Input.jsx'
import OptionCard from '../../components/ui/OptionCard.jsx'
import MultiChipToggle from '../../components/ui/MultiChipToggle.jsx'

const PRIMARY_GOALS = [
  { value: 'lose_weight', label: 'Lose weight', description: 'Reduce body fat while preserving muscle' },
  { value: 'build_muscle', label: 'Build muscle', description: 'Gain lean mass through progressive training' },
  { value: 'improve_endurance', label: 'Improve endurance', description: 'Build cardiovascular capacity' },
  { value: 'general_health', label: 'General health', description: 'Feel better and move more overall' },
  { value: 'sport_specific', label: 'Sport-specific performance', description: 'Train for a particular sport' },
]

const SECONDARY_GOALS = [
  { value: 'improve_sleep', label: 'Improve sleep' },
  { value: 'reduce_stress', label: 'Reduce stress' },
  { value: 'increase_flexibility', label: 'Increase flexibility' },
  { value: 'build_consistency', label: 'Build consistency' },
]

export default function GoalsStep({ defaultValues, onBack, onNext, stepIndex, stepCount, saving }) {
  const { control, handleSubmit, watch, setValue, formState: { isValid } } = useForm({
    mode: 'onChange',
    defaultValues: {
      primary_goal: defaultValues?.primary_goal || '',
      target_timeline_weeks: defaultValues?.target_timeline_weeks || 12,
      secondary_goals: defaultValues?.secondary_goals || [],
    },
  })

  const primaryGoal = watch('primary_goal')
  const secondaryGoals = watch('secondary_goals')

  const toggleSecondary = (value) => {
    const current = secondaryGoals || []
    setValue(
      'secondary_goals',
      current.includes(value) ? current.filter((v) => v !== value) : [...current, value],
      { shouldValidate: true }
    )
  }

  return (
    <OnboardingLayout
      stepIndex={stepIndex}
      stepCount={stepCount}
      stepLabel={`Step ${stepIndex} of ${stepCount} — Goals`}
      title="What's your main goal?"
      subtitle="This shapes the entire structure of your plan."
      onBack={onBack}
      onNext={handleSubmit(onNext)}
      showBack={stepIndex > 1 || stepCount === 1}
      nextDisabled={!primaryGoal}
      nextLoading={saving}
    >
      <div className="space-y-lg">
        <div className="grid gap-sm">
          {PRIMARY_GOALS.map((g) => (
            <Controller
              key={g.value}
              name="primary_goal"
              control={control}
              rules={{ required: true }}
              render={({ field }) => (
                <OptionCard
                  label={g.label}
                  description={g.description}
                  selected={field.value === g.value}
                  onSelect={() => field.onChange(g.value)}
                />
              )}
            />
          ))}
        </div>

        <div>
          <span className="block mb-sm text-label-md text-on-surface-variant">Target timeline</span>
          <Controller
            name="target_timeline_weeks"
            control={control}
            render={({ field }) => (
              <Input
                type="number"
                min={1}
                max={104}
                value={field.value}
                onChange={(e) => field.onChange(Number(e.target.value))}
                placeholder="Weeks"
              />
            )}
          />
        </div>

        <div>
          <span className="block mb-sm text-label-md text-on-surface-variant">
            Anything else you'd like to work on? (optional)
          </span>
          <MultiChipToggle options={SECONDARY_GOALS} selected={secondaryGoals || []} onToggle={toggleSecondary} />
        </div>
      </div>
    </OnboardingLayout>
  )
}
