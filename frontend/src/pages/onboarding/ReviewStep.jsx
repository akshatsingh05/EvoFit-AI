import OnboardingLayout from '../../layouts/OnboardingLayout.jsx'
import Card from '../../components/ui/Card.jsx'

export function SummaryRow({ label, value }) {
  if (value === undefined || value === null || value === '') return null
  return (
    <div className="flex justify-between py-sm border-b border-divider last:border-none">
      <span className="text-body-sm text-on-surface-variant">{label}</span>
      <span className="text-body-sm text-on-surface font-medium text-right max-w-[60%]">
        {Array.isArray(value) ? (value.length ? value.join(', ') : '—') : String(value)}
      </span>
    </div>
  )
}

export default function ReviewStep({ data, onBack, onNext, stepIndex, stepCount, saving }) {
  const { goals, body_metrics: bodyMetrics, fitness_experience: fitnessExperience, lifestyle_diet: lifestyleDiet, medical_history: medicalHistory } = data

  return (
    <OnboardingLayout
      stepIndex={stepIndex}
      stepCount={stepCount}
      stepLabel={`Step ${stepIndex} of ${stepCount} — Review`}
      title="Review your profile"
      subtitle="This is what your AI coach will use to build your first plan."
      onBack={onBack}
      onNext={onNext}
      nextLabel="Finish & go to dashboard"
      nextLoading={saving}
    >
      <div className="space-y-md">
        <Card>
          <h3 className="text-label-lg font-display mb-sm">Goals</h3>
          <SummaryRow label="Primary goal" value={goals?.primary_goal} />
          <SummaryRow label="Timeline (weeks)" value={goals?.target_timeline_weeks} />
          <SummaryRow label="Also working on" value={goals?.secondary_goals} />
        </Card>

        <Card>
          <h3 className="text-label-lg font-display mb-sm">Body metrics</h3>
          <SummaryRow label="Height" value={bodyMetrics?.height_cm ? `${bodyMetrics.height_cm} cm` : null} />
          <SummaryRow label="Weight" value={bodyMetrics?.weight_kg ? `${bodyMetrics.weight_kg} kg` : null} />
          <SummaryRow label="Age" value={bodyMetrics?.age} />
          <SummaryRow label="Sex" value={bodyMetrics?.sex} />
        </Card>

        <Card>
          <h3 className="text-label-lg font-display mb-sm">Fitness experience</h3>
          <SummaryRow label="Level" value={fitnessExperience?.experience_level} />
          <SummaryRow label="Current workouts / week" value={fitnessExperience?.workouts_per_week_current} />
          <SummaryRow label="Equipment" value={fitnessExperience?.equipment_access} />
          <SummaryRow label="Preferred types" value={fitnessExperience?.preferred_workout_types} />
        </Card>

        <Card>
          <h3 className="text-label-lg font-display mb-sm">Lifestyle & diet</h3>
          <SummaryRow label="Diet type" value={lifestyleDiet?.diet_type} />
          <SummaryRow label="Meals / day" value={lifestyleDiet?.meals_per_day} />
          <SummaryRow label="Avg sleep" value={lifestyleDiet?.sleep_hours_avg ? `${lifestyleDiet.sleep_hours_avg} hrs` : null} />
          <SummaryRow label="Stress level" value={lifestyleDiet?.stress_level} />
          <SummaryRow label="Daily activity" value={lifestyleDiet?.occupation_activity} />
        </Card>

        <Card>
          <h3 className="text-label-lg font-display mb-sm">Medical history</h3>
          <SummaryRow label="Conditions" value={medicalHistory?.conditions} />
          <SummaryRow label="Injuries" value={medicalHistory?.injuries} />
          <SummaryRow label="Medications" value={medicalHistory?.medications} />
          <SummaryRow label="Cleared for exercise" value={medicalHistory?.cleared_for_exercise ? 'Yes' : 'No'} />
        </Card>
      </div>
    </OnboardingLayout>
  )
}
