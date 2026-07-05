import Card from '../ui/Card.jsx'

export default function AICoachRecommendations({ recommendations }) {
  if (!recommendations || recommendations.length === 0) return null

  return (
    <Card>
      <h3 className="text-label-lg font-display text-on-surface mb-md">AI Coach Recommendations</h3>
      <ul className="space-y-sm">
        {recommendations.map((rec, i) => (
          <li key={i} className="flex items-start gap-sm text-body-md text-on-surface-variant">
            <span className="text-primary mt-xs" aria-hidden>•</span>
            <span>{rec}</span>
          </li>
        ))}
      </ul>
    </Card>
  )
}
