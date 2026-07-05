import { Link } from 'react-router-dom'
import Card from '../ui/Card.jsx'

export default function RecoveryScoreCard({ score }) {
  return (
    <Card>
      <h3 className="text-label-lg font-display text-on-surface mb-sm">Recovery Score</h3>
      {score === null ? (
        <>
          <p className="text-headline-md text-on-surface-variant">—</p>
          <p className="text-body-sm text-on-surface-variant mt-xs">
            <Link to="/checkin" className="text-secondary">Complete a check-in</Link> to get your first score.
          </p>
        </>
      ) : (
        <p className="text-headline-md text-primary">
          {score}
          <span className="text-body-md text-on-surface-variant">/100</span>
        </p>
      )}
    </Card>
  )
}
