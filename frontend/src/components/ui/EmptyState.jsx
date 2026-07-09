import { motion } from 'framer-motion'
import Button from './Button.jsx'

/**
 * Consistent empty state used across history, imports, reports,
 * notifications, etc. `Icon` is any lucide-react icon component.
 */
export default function EmptyState({
  icon: Icon,
  title,
  message,
  actionLabel,
  onAction,
  actionTo,
  className = '',
}) {
  const action = actionLabel ? (
    actionTo ? (
      <Button as="a" href={actionTo} variant="primary">
        {actionLabel}
      </Button>
    ) : (
      <Button variant="primary" onClick={onAction}>
        {actionLabel}
      </Button>
    )
  ) : null

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`flex flex-col items-center text-center py-xxl px-lg ${className}`}
      role="status"
    >
      {Icon ? (
        <span className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10 text-primary mb-lg">
          <Icon size={28} aria-hidden="true" />
        </span>
      ) : null}
      <h3 className="text-headline-sm text-on-surface mb-sm">{title}</h3>
      {message ? (
        <p className="text-body-md text-on-surface-variant max-w-[380px] mb-lg">{message}</p>
      ) : null}
      {action}
    </motion.div>
  )
}
