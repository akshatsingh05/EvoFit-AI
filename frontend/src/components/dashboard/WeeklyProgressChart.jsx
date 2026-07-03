import Card from '../ui/Card.jsx'

export default function WeeklyProgressChart({ points }) {
  const maxValue = Math.max(1, ...points.map((p) => p.workouts_completed))
  const barWidth = 32
  const gap = 20
  const chartHeight = 120
  const width = points.length * (barWidth + gap)

  const allZero = points.every((p) => p.workouts_completed === 0)

  return (
    <Card>
      <h3 className="text-label-lg font-display text-on-surface mb-md">Weekly Progress</h3>

      {allZero ? (
        <p className="text-body-sm text-on-surface-variant mb-md">
          No workouts logged yet this week — this fills in once check-ins (Module 4) are live.
        </p>
      ) : null}

      <svg viewBox={`0 0 ${width} ${chartHeight + 24}`} className="w-full" role="img" aria-label="Weekly workout progress">
        {points.map((p, i) => {
          const barHeight = allZero ? 4 : (p.workouts_completed / maxValue) * chartHeight
          const x = i * (barWidth + gap)
          return (
            <g key={p.day_label}>
              <rect
                x={x}
                y={chartHeight - barHeight}
                width={barWidth}
                height={Math.max(barHeight, 4)}
                rx={6}
                className={allZero ? 'fill-surface-container-high' : 'fill-primary'}
              />
              <text
                x={x + barWidth / 2}
                y={chartHeight + 18}
                textAnchor="middle"
                className="fill-on-surface-variant"
                style={{ fontSize: '11px', fontFamily: 'Inter, sans-serif' }}
              >
                {p.day_label}
              </text>
            </g>
          )
        })}
      </svg>
    </Card>
  )
}
