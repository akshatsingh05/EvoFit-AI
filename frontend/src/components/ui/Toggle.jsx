export default function Toggle({ checked, onChange, label, description }) {
  return (
    <label className="flex items-center justify-between gap-md py-sm cursor-pointer">
      <span>
        <span className="block text-body-md text-on-surface">{label}</span>
        {description ? <span className="block text-body-sm text-on-surface-variant">{description}</span> : null}
      </span>
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        onClick={() => onChange(!checked)}
        className={`
          relative h-7 w-12 rounded-full transition-colors duration-150 shrink-0
          ${checked ? 'bg-primary' : 'bg-surface-container-high'}
        `}
      >
        <span
          className={`
            absolute top-1 h-5 w-5 rounded-full bg-surface-container-lowest shadow-card transition-transform duration-150
            ${checked ? 'translate-x-6' : 'translate-x-1'}
          `}
        />
      </button>
    </label>
  )
}
