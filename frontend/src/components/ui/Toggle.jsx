export default function Toggle({ checked, onChange, label, description, disabled = false }) {
  return (
    <label
      className={`flex items-center justify-between gap-md py-sm ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
    >
      <span>
        <span className="block text-body-md text-on-surface">{label}</span>
        {description ? <span className="block text-body-sm text-on-surface-variant">{description}</span> : null}
      </span>
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        disabled={disabled}
        onClick={() => onChange(!checked)}
        className={`
          relative inline-flex h-6 w-11 shrink-0 items-center rounded-full
          transition-colors duration-150 ease-in-out
          focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary
          disabled:cursor-not-allowed
          ${checked ? 'bg-primary' : 'bg-surface-container-high'}
        `}
      >
        <span
          className={`
            pointer-events-none inline-block h-4 w-4 transform rounded-full
            bg-surface-container-lowest shadow-card
            transition-transform duration-150 ease-in-out
            ${checked ? 'translate-x-6' : 'translate-x-1'}
          `}
        />
      </button>
    </label>
  )
}
