import Card from '../ui/Card.jsx'

export default function ProgressChart({ title, points, unit, emptyMessage }) {
  if (!points || points.length === 0) {
    return (
      <Card>
        <h3 className="text-label-lg font-display text-on-surface mb-sm">{title}</h3>
        <p className="text-body-sm text-on-surface-variant">{emptyMessage}</p>
      </Card>
    )
  }

  const values = points.map((p) => p.value)
  const min = Math.min(...values)
  const max = Math.max(...values)
  const range = max - min || 1
  const width = 560
  const height = 140
  const padding = 24

  const coords = points.map((p, i) => {
    const x = padding + (i / Math.max(points.length - 1, 1)) * (width - padding * 2)
    const y = height - padding - ((p.value - min) / range) * (height - padding * 2)
    return { x, y, ...p }
  })

  const pathD = coords.map((c, i) => `${i === 0 ? 'M' : 'L'} ${c.x} ${c.y}`).join(' ')

  return (
    <Card>
      <h3 className="text-label-lg font-display text-on-surface mb-md">{title}</h3>
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full" role="img" aria-label={title}>
        <path d={pathD} fill="none" className="stroke-primary" strokeWidth="2.5" />
        {coords.map((c) => (
          <circle key={c.label} cx={c.x} cy={c.y} r={3.5} className="fill-primary" />
        ))}
        {coords.map((c) => (
          <text
            key={`label-${c.label}`}
            x={c.x}
            y={height - 4}
            textAnchor="middle"
            className="fill-on-surface-variant"
            style={{ fontSize: '10px', fontFamily: 'Inter, sans-serif' }}
          >
            {c.label}
          </text>
        ))}
      </svg>
      <p className="text-body-sm text-on-surface-variant mt-xs">
        Latest: {values[values.length - 1]}{unit}
      </p>
    </Card>
  )
}
