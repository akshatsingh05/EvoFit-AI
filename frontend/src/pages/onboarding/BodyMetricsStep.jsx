import { useForm, Controller } from 'react-hook-form'
import OnboardingLayout from '../../layouts/OnboardingLayout.jsx'
import Input from '../../components/ui/Input.jsx'
import OptionCard from '../../components/ui/OptionCard.jsx'

const SEX_OPTIONS = [
  { value: 'female', label: 'Female' },
  { value: 'male', label: 'Male' },
  { value: 'other', label: 'Other' },
]

export default function BodyMetricsStep({ defaultValues, onBack, onNext, stepIndex, stepCount, saving }) {
  const {
    register,
    control,
    handleSubmit,
    watch,
    formState: { errors, isValid },
  } = useForm({
    mode: 'onChange',
    defaultValues: {
      height_cm: defaultValues?.height_cm || '',
      weight_kg: defaultValues?.weight_kg || '',
      target_weight_kg: defaultValues?.target_weight_kg || '',
      age: defaultValues?.age || '',
      sex: defaultValues?.sex || '',
    },
  })

  const sex = watch('sex')

  const submit = (values) =>
    onNext({
      ...values,
      height_cm: Number(values.height_cm),
      weight_kg: Number(values.weight_kg),
      target_weight_kg: values.target_weight_kg ? Number(values.target_weight_kg) : null,
      age: Number(values.age),
    })

  return (
    <OnboardingLayout
      stepIndex={stepIndex}
      stepCount={stepCount}
      stepLabel={`Step ${stepIndex} of ${stepCount} — Body metrics`}
      title="Tell us about your body"
      subtitle="Used to calculate calorie needs and set safe training loads."
      onBack={onBack}
      onNext={handleSubmit(submit)}
      nextDisabled={!isValid}
      nextLoading={saving}
    >
      <div className="space-y-lg">
        <div className="grid grid-cols-2 gap-md">
          <Input
            label="Height (cm)"
            type="number"
            error={errors.height_cm?.message}
            {...register('height_cm', { required: 'Required', min: { value: 1, message: 'Invalid' } })}
          />
          <Input
            label="Age"
            type="number"
            error={errors.age?.message}
            {...register('age', { required: 'Required', min: { value: 13, message: 'Must be 13+' } })}
          />
          <Input
            label="Current weight (kg)"
            type="number"
            error={errors.weight_kg?.message}
            {...register('weight_kg', { required: 'Required', min: { value: 1, message: 'Invalid' } })}
          />
          <Input
            label="Target weight (kg, optional)"
            type="number"
            {...register('target_weight_kg')}
          />
        </div>

        <div>
          <span className="block mb-sm text-label-md text-on-surface-variant">Sex</span>
          <div className="grid grid-cols-3 gap-sm">
            {SEX_OPTIONS.map((opt) => (
              <Controller
                key={opt.value}
                name="sex"
                control={control}
                rules={{ required: true }}
                render={({ field }) => (
                  <OptionCard label={opt.label} selected={field.value === opt.value} onSelect={() => field.onChange(opt.value)} />
                )}
              />
            ))}
          </div>
        </div>
      </div>
    </OnboardingLayout>
  )
}
