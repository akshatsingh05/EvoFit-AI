import Card from '../ui/Card.jsx'

function formatDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
}

/**
 * Shared between Workout and Nutrition (Sprint 2 requirement #6). `extraFields`
 * lets each page add its one domain-specific line (workout days / calories
 * target) without forking the component.
 */
export default function PlanInfoCard({ planInfo, extraFields = [] }) {
  if (!planInfo) return null

  const fields = [
    { label: 'Generated on', value: formatDate(planInfo.generated_on) },
    { label: 'Current goal', value: planInfo.current_goal ? planInfo.current_goal.replace(/_/g, ' ') : '—' },
    ...(planInfo.difficulty ? [{ label: 'Difficulty', value: planInfo.difficulty }] : []),
    ...extraFields,
    { label: 'Plan version', value: `v${planInfo.plan_version}` },
    { label: 'Last regenerated', value: planInfo.last_regenerated_at ? formatDate(planInfo.last_regenerated_at) : 'Not yet regenerated' },
  ]

  return (
    <Card className="mb-lg">
      <h3 className="text-label-lg font-display text-on-surface-variant mb-sm">Why you got this plan</h3>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-md">
        {fields.map((f) => (
          <div key={f.label}>
            <p className="text-body-sm text-on-surface-variant">{f.label}</p>
            <p className="text-body-md text-on-surface font-medium capitalize">{f.value}</p>
          </div>
        ))}
      </div>
    </Card>
  )
}
