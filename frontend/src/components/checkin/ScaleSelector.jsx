export default function ScaleSelector({ label, value, onChange, min = 1, max = 5, lowLabel, highLabel }) {
  const options = Array.from({ length: max - min + 1 }, (_, i) => min + i)

  return (
    <div>
      <span className="block mb-sm text-label-md text-on-surface-variant">{label}</span>
      <div className="flex gap-sm">
        {options.map((n) => (
          <button
            key={n}
            type="button"
            onClick={() => onChange(n)}
            aria-pressed={value === n}
            className={`
              h-11 flex-1 rounded-md text-label-lg font-display transition-colors
              focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary
              ${value === n ? 'bg-primary text-on-primary' : 'bg-surface-container text-on-surface-variant hover:bg-surface-container-high'}
            `}
          >
            {n}
          </button>
        ))}
      </div>
      {lowLabel || highLabel ? (
        <div className="flex justify-between mt-xs text-body-sm text-on-surface-variant">
          <span>{lowLabel}</span>
          <span>{highLabel}</span>
        </div>
      ) : null}
    </div>
  )
}
