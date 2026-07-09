import { motion } from 'framer-motion'

/**
 * `hoverable` adds a gentle lift on hover — used for clickable/interactive
 * cards (dashboard widgets, plan cards). Static informational cards should
 * leave it off.
 */
export default function Card({ children, className = '', padded = true, hoverable = false, ...rest }) {
  const classes = `
    bg-surface-container-lowest rounded-lg shadow-card border border-transparent
    ${hoverable ? 'transition-shadow hover:shadow-elevated hover:border-outline-variant/40' : ''}
    ${padded ? 'p-lg' : ''}
    ${className}
  `

  if (hoverable) {
    return (
      <motion.div
        whileHover={{ y: -2 }}
        transition={{ duration: 0.18, ease: 'easeOut' }}
        className={classes}
        {...rest}
      >
        {children}
      </motion.div>
    )
  }

  return (
    <div className={classes} {...rest}>
      {children}
    </div>
  )
}
