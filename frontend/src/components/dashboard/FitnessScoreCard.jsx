import Card from '../ui/Card.jsx'

export default function FitnessScoreCard({ score, basis }) {
  return (
    <Card>
      <h3 className="text-label-lg font-display text-on-surface mb-sm">Fitness Score</h3>
      <p className="text-headline-md text-secondary">
        {score}
        <span className="text-body-md text-on-surface-variant">/100</span>
      </p>
      <p className="text-body-sm text-on-surface-variant mt-xs">{basis}</p>
    </Card>
  )
}
