import { useEffect, useMemo, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { PartyPopper } from 'lucide-react'

const COLORS = ['#00E676', '#22C55E', '#2170E4', '#EF9900', '#FFFFFF']

/**
 * Fires a brief confetti burst + achievement card. Mount conditionally:
 *   {showCelebration && <Celebration title="7-day streak!" message="..." onDone={() => setShowCelebration(false)} />}
 */
export default function Celebration({ title, message, onDone, duration = 2600 }) {
  const [visible, setVisible] = useState(true)

  useEffect(() => {
    const timer = setTimeout(() => setVisible(false), duration)
    return () => clearTimeout(timer)
  }, [duration])

  const pieces = useMemo(
    () =>
      Array.from({ length: 24 }).map((_, i) => ({
        id: i,
        left: Math.random() * 100,
        delay: Math.random() * 0.4,
        duration: 1 + Math.random() * 0.8,
        color: COLORS[i % COLORS.length],
      })),
    []
  )

  return (
    <AnimatePresence onExitComplete={onDone}>
      {visible && (
      <motion.div
        className="fixed inset-0 z-50 flex items-center justify-center pointer-events-none"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
      >
        <div className="absolute inset-x-0 top-0 h-40 overflow-hidden" aria-hidden="true">
          {pieces.map((p) => (
            <span
              key={p.id}
              className="absolute top-0 h-2 w-2 rounded-sm"
              style={{
                left: `${p.left}%`,
                backgroundColor: p.color,
                animation: `confetti-fall ${p.duration}s ease-in forwards`,
                animationDelay: `${p.delay}s`,
              }}
            />
          ))}
        </div>
        <motion.div
          role="status"
          initial={{ scale: 0.85, opacity: 0, y: 12 }}
          animate={{ scale: 1, opacity: 1, y: 0 }}
          exit={{ scale: 0.9, opacity: 0 }}
          transition={{ type: 'spring', stiffness: 300, damping: 22 }}
          className="pointer-events-auto bg-surface-container-lowest rounded-lg shadow-elevated px-xl py-lg flex items-center gap-md max-w-[360px]"
        >
          <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
            <PartyPopper size={22} aria-hidden="true" />
          </span>
          <div>
            <p className="text-headline-sm text-on-surface">{title}</p>
            {message ? <p className="text-body-sm text-on-surface-variant mt-1">{message}</p> : null}
          </div>
        </motion.div>
      </motion.div>
      )}
    </AnimatePresence>
  )
}
