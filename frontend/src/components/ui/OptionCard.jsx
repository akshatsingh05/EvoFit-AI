export default function OptionCard({ label, description, selected, onSelect }) {
  return (
    <button
      type="button"
      onClick={onSelect}
      aria-pressed={selected}
      className={`
        w-full text-left p-md rounded-md border-2 transition-colors duration-150
        focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary
        ${selected
          ? 'border-primary bg-primary-container/10'
          : 'border-outline-variant bg-surface-container-lowest hover:border-outline'}
      `}
    >
      <span className="block font-display text-label-lg text-on-surface">{label}</span>
      {description ? (
        <span className="block mt-xs text-body-sm text-on-surface-variant">{description}</span>
      ) : null}
    </button>
  )
}
