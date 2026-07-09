import { motion } from 'framer-motion'

const VARIANTS = {
  primary: 'bg-primary text-on-primary hover:bg-on-primary-fixed-variant shadow-sm hover:shadow-md',
  secondary: 'bg-transparent text-secondary border border-secondary hover:bg-secondary/5',
  ghost: 'bg-transparent text-on-surface-variant hover:bg-surface-container',
  danger: 'bg-error text-on-error hover:opacity-90 shadow-sm',
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
  as,
  href,
  ...rest
}) {
  const isDisabled = disabled || loading
  const classes = `
    inline-flex items-center justify-center gap-sm
    font-display font-label-lg text-label-lg
    rounded-full px-lg h-[52px]
    transition-colors duration-150
    focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary
    disabled:opacity-50 disabled:cursor-not-allowed
    ${fullWidth ? 'w-full' : ''}
    ${VARIANTS[variant]}
    ${className}
  `

  const content = (
    <>
      {loading ? (
        <span
          className="h-4 w-4 rounded-full border-2 border-current border-t-transparent animate-spin"
          aria-hidden="true"
        />
      ) : null}
      {children}
    </>
  )

  const motionProps = isDisabled
    ? {}
    : { whileTap: { scale: 0.97 }, whileHover: { scale: 1.01 } }

  if (as === 'a' && href) {
    return (
      <motion.a href={href} className={classes} aria-disabled={isDisabled || undefined} {...motionProps} {...rest}>
        {content}
      </motion.a>
    )
  }

  return (
    <motion.button
      type={type}
      disabled={isDisabled}
      onClick={onClick}
      aria-busy={loading || undefined}
      className={classes}
      {...motionProps}
      {...rest}
    >
      {content}
    </motion.button>
  )
}
