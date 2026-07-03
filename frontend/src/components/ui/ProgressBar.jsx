export default function ProgressBar({ value, max, label }) {
  const pct = Math.min(100, Math.round((value / max) * 100))
  return (
    <div>
      {label ? (
        <div className="flex justify-between mb-sm">
          <span className="text-label-md text-on-surface-variant">{label}</span>
          <span className="text-label-md text-on-surface-variant">{pct}%</span>
        </div>
      ) : null}
      <div className="h-[8px] w-full rounded-full bg-surface-container-high overflow-hidden">
        <div
          className="h-full rounded-full bg-primary transition-all duration-300"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}
