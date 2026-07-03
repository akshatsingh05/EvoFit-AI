import Card from '../ui/Card.jsx'

export default function RecoveryScoreCard({ score }) {
  return (
    <Card>
      <h3 className="text-label-lg font-display text-on-surface mb-sm">Recovery Score</h3>
      {score === null ? (
        <>
          <p className="text-headline-md text-on-surface-variant">—</p>
          <p className="text-body-sm text-on-surface-variant mt-xs">
            Available once daily check-ins start (Module 4).
          </p>
        </>
      ) : (
        <p className="text-headline-md text-primary">{score}<span className="text-body-md text-on-surface-variant">/100</span></p>
      )}
    </Card>
  )
}
