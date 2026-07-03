import { useForm, Controller } from 'react-hook-form'
import OnboardingLayout from '../../layouts/OnboardingLayout.jsx'
import MultiChipToggle from '../../components/ui/MultiChipToggle.jsx'
import OptionCard from '../../components/ui/OptionCard.jsx'

const COMMON_CONDITIONS = [
  { value: 'asthma', label: 'Asthma' },
  { value: 'diabetes_type_1', label: 'Diabetes (Type 1)' },
  { value: 'diabetes_type_2', label: 'Diabetes (Type 2)' },
  { value: 'hypertension', label: 'High blood pressure' },
  { value: 'heart_condition', label: 'Heart condition' },
  { value: 'none', label: 'None of these' },
]

const COMMON_INJURIES = [
  { value: 'lower_back', label: 'Lower back' },
  { value: 'left_knee', label: 'Left knee' },
  { value: 'right_knee', label: 'Right knee' },
  { value: 'shoulder', label: 'Shoulder' },
  { value: 'ankle', label: 'Ankle' },
  { value: 'none', label: 'None of these' },
]

export default function MedicalHistoryStep({ defaultValues, onBack, onNext, stepIndex, stepCount, saving }) {
  const { register, control, handleSubmit, watch, setValue } = useForm({
    defaultValues: {
      conditions: defaultValues?.conditions || [],
      injuries: defaultValues?.injuries || [],
      medications: defaultValues?.medications || '',
      allergies: defaultValues?.allergies || '',
      additional_notes: defaultValues?.additional_notes || '',
      cleared_for_exercise: defaultValues?.cleared_for_exercise ?? true,
    },
  })

  const conditions = watch('conditions')
  const injuries = watch('injuries')
  const clearedForExercise = watch('cleared_for_exercise')

  const toggleFrom = (field, list) => (value) => {
    const current = list || []
    setValue(field, current.includes(value) ? current.filter((v) => v !== value) : [...current, value])
  }

  return (
    <OnboardingLayout
      stepIndex={stepIndex}
      stepCount={stepCount}
      stepLabel={`Step ${stepIndex} of ${stepCount} — Medical history`}
      title="Anything we should train around?"
      subtitle="This keeps your plan safe. It's never shared and only used to adjust recommendations."
      onBack={onBack}
      onNext={handleSubmit(onNext)}
      nextLoading={saving}
    >
      <div className="space-y-lg">
        <div>
          <span className="block mb-sm text-label-md text-on-surface-variant">Existing conditions</span>
          <MultiChipToggle options={COMMON_CONDITIONS} selected={conditions || []} onToggle={toggleFrom('conditions', conditions)} />
        </div>

        <div>
          <span className="block mb-sm text-label-md text-on-surface-variant">Injuries to work around</span>
          <MultiChipToggle options={COMMON_INJURIES} selected={injuries || []} onToggle={toggleFrom('injuries', injuries)} />
        </div>

        <label className="block">
          <span className="block mb-sm text-label-md text-on-surface-variant">Current medications (optional)</span>
          <textarea
            className="w-full min-h-[80px] p-md bg-input-fill rounded-md text-body-md focus:outline-none focus:ring-2 focus:ring-primary"
            placeholder="List any medications that may affect training or recovery"
            {...register('medications')}
          />
        </label>

        <label className="block">
          <span className="block mb-sm text-label-md text-on-surface-variant">Allergies (optional)</span>
          <textarea
            className="w-full min-h-[60px] p-md bg-input-fill rounded-md text-body-md focus:outline-none focus:ring-2 focus:ring-primary"
            placeholder="Food or environmental allergies"
            {...register('allergies')}
          />
        </label>

        <label className="block">
          <span className="block mb-sm text-label-md text-on-surface-variant">Anything else? (optional)</span>
          <textarea
            className="w-full min-h-[60px] p-md bg-input-fill rounded-md text-body-md focus:outline-none focus:ring-2 focus:ring-primary"
            {...register('additional_notes')}
          />
        </label>

        <div>
          <span className="block mb-sm text-label-md text-on-surface-variant">
            Has a doctor cleared you for exercise?
          </span>
          <div className="grid grid-cols-2 gap-sm">
            <Controller
              name="cleared_for_exercise"
              control={control}
              render={({ field }) => (
                <>
                  <OptionCard label="Yes" selected={field.value === true} onSelect={() => field.onChange(true)} />
                  <OptionCard label="Not sure / No" selected={field.value === false} onSelect={() => field.onChange(false)} />
                </>
              )}
            />
          </div>
        </div>
      </div>
    </OnboardingLayout>
  )
}
