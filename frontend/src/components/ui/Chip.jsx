const COLOR_MAP = {
  primary: 'bg-primary/10 text-primary',
  secondary: 'bg-secondary/10 text-secondary',
  tertiary: 'bg-tertiary/10 text-tertiary',
  neutral: 'bg-surface-container-high text-on-surface-variant',
}

export default function Chip({ children, color = 'primary', onRemove, className = '' }) {
  return (
    <span
      className={`inline-flex items-center gap-xs px-md h-8 rounded-full text-label-md font-body ${COLOR_MAP[color]} ${className}`}
    >
      {children}
      {onRemove ? (
        <button
          type="button"
          onClick={onRemove}
          aria-label="Remove"
          className="ml-xs leading-none opacity-70 hover:opacity-100"
        >
          ×
        </button>
      ) : null}
    </span>
  )
}
