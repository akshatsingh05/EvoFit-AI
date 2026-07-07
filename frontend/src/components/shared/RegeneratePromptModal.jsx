import { useEffect, useRef } from 'react'
import Button from '../ui/Button.jsx'
import Card from '../ui/Card.jsx'

/**
 * Shown after a profile edit that could affect AI-generated plans.
 * Shared between Workout and Nutrition regeneration flows so there is a
 * single place that owns this copy/behavior (Sprint 2 requirement #7).
 */
export default function RegeneratePromptModal({ open, onRegenerate, onLater, regenerating }) {
  const headingRef = useRef(null)

  useEffect(() => {
    if (open) headingRef.current?.focus()
  }, [open])

  if (!open) return null

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-container"
      onKeyDown={(e) => {
        if (e.key === 'Escape') onLater?.()
      }}
    >
      <Card role="dialog" aria-modal="true" aria-labelledby="regenerate-prompt-title" className="max-w-[420px] w-full">
        <h2 id="regenerate-prompt-title" ref={headingRef} tabIndex={-1} className="text-headline-sm text-on-surface mb-sm outline-none">
          Your profile has changed
        </h2>
        <p className="text-body-md text-on-surface-variant mb-lg">
          Your workout and nutrition plans may no longer be optimal. Would you like to regenerate them?
        </p>
        <div className="flex gap-sm justify-end">
          <Button variant="ghost" onClick={onLater} disabled={regenerating}>
            Later
          </Button>
          <Button variant="primary" onClick={onRegenerate} loading={regenerating}>
            Regenerate Now
          </Button>
        </div>
      </Card>
    </div>
  )
}
