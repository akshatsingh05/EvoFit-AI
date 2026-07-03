import Card from '../ui/Card.jsx'

export default function AICoachTipCard({ tip }) {
  return (
    <Card className="bg-primary-container/10">
      <div className="flex items-start gap-md">
        <span className="h-9 w-9 rounded-full bg-primary/15 text-primary flex items-center justify-center shrink-0">✦</span>
        <div>
          <h3 className="text-label-lg font-display text-on-surface mb-xs">AI Coach Tip</h3>
          <p className="text-body-md text-on-surface-variant">{tip}</p>
        </div>
      </div>
    </Card>
  )
}
