const VARIANTS = {
  primary: 'bg-primary text-on-primary hover:bg-on-primary-fixed-variant active:scale-[0.98]',
  secondary: 'bg-transparent text-secondary border border-secondary hover:bg-secondary/5 active:scale-[0.98]',
  ghost: 'bg-transparent text-on-surface-variant hover:bg-surface-container active:scale-[0.98]',
}

export default function Button({
  children,
  variant = 'primary',
  type = 'button',
  disabled = false,
  loading = false,
  onClick,
  className = '',
  fullWidth = false,
}) {
  return (
    <button
      type={type}
      disabled={disabled || loading}
      onClick={onClick}
      className={`
        inline-flex items-center justify-center gap-sm
        font-display font-label-lg text-label-lg
        rounded-full px-lg h-[52px]
        transition-all duration-150
        focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary
        disabled:opacity-50 disabled:cursor-not-allowed
        ${fullWidth ? 'w-full' : ''}
        ${VARIANTS[variant]}
        ${className}
      `}
    >
      {loading ? (
        <span className="h-4 w-4 rounded-full border-2 border-current border-t-transparent animate-spin" />
      ) : null}
      {children}
    </button>
  )
}
