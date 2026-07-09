import { memo, useState } from 'react'
import { RefreshCw } from 'lucide-react'

function ExerciseCard({ exercise, index, onReplace, replacing }) {
  const [open, setOpen] = useState(false)

  return (
    <div className="flex items-start gap-md py-md border-b border-divider last:border-none">
      <span className="h-8 w-8 rounded-full bg-primary/10 text-primary flex items-center justify-center text-label-md font-display shrink-0">
        {index + 1}
      </span>
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-sm">
          <h4 className="text-label-lg font-display text-on-surface">{exercise.name}</h4>
          {onReplace ? (
            <button
              type="button"
              onClick={() => setOpen((o) => !o)}
              disabled={replacing}
              className="shrink-0 flex items-center gap-xs text-body-sm text-primary hover:underline disabled:opacity-50"
            >
              <RefreshCw className={`h-4 w-4 ${replacing ? 'animate-spin' : ''}`} />
              Replace
            </button>
          ) : null}
        </div>
        <div className="flex flex-wrap gap-md mt-xs text-body-sm text-on-surface-variant">
          <span>{exercise.sets} sets</span>
          <span>{exercise.reps} reps</span>
          <span>{exercise.rest_seconds}s rest</span>
        </div>
        <p className="text-body-sm text-on-surface-variant mt-xs">{exercise.instructions}</p>

        {open && onReplace ? (
          <div className="flex gap-sm mt-sm">
            <button
              type="button"
              className="h-8 px-md rounded-full bg-surface-container text-label-md text-on-surface-variant hover:bg-surface-container-high"
              onClick={() => {
                setOpen(false)
                onReplace(null)
              }}
            >
              Swap (surprise me)
            </button>
            <button
              type="button"
              className="h-8 px-md rounded-full bg-surface-container text-label-md text-on-surface-variant hover:bg-surface-container-high"
              onClick={() => setOpen(false)}
            >
              Cancel
            </button>
          </div>
        ) : null}
      </div>
    </div>
  )
}

export default memo(ExerciseCard)
