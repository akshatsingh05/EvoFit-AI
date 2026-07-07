import { useMemo } from 'react'

const WEEKDAY_LABELS = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']

function toIso(d) {
  return d.toISOString().slice(0, 10)
}

function startOfMonthGrid(year, month) {
  // month is 0-indexed. Returns the Monday on/before the 1st of the month.
  const first = new Date(year, month, 1)
  const dayOfWeek = (first.getDay() + 6) % 7 // 0 = Monday
  const gridStart = new Date(first)
  gridStart.setDate(first.getDate() - dayOfWeek)
  return gridStart
}

/**
 * Domain-agnostic month calendar. Callers supply:
 * - `year`/`month` (0-indexed) to control which month is shown
 * - `dayStatus` — a map of ISO date string -> {status, ...anything}, used only
 *   to pick a dot color via `statusColors`
 * - `onSelectDay(isoDate)` — called when a day is clicked
 * - `renderBadge(dayInfo)` — optional, e.g. a streak flame icon on today
 *
 * This component knows nothing about workouts, meals, or check-ins — the
 * Workout page is just the first caller (Sprint 2 requirement: reusable for
 * Nutrition / Daily Check-In / Recovery later without rewriting it).
 */
export default function Calendar({
  year,
  month,
  selectedDate,
  dayStatus = {},
  statusColors = {},
  minDate,
  onSelectDay,
}) {
  const weeks = useMemo(() => {
    const gridStart = startOfMonthGrid(year, month)
    const result = []
    let cursor = new Date(gridStart)
    for (let w = 0; w < 6; w++) {
      const week = []
      for (let d = 0; d < 7; d++) {
        week.push(new Date(cursor))
        cursor.setDate(cursor.getDate() + 1)
      }
      result.push(week)
    }
    return result
  }, [year, month])

  const todayIso = toIso(new Date())

  return (
    <div>
      <div className="grid grid-cols-7 gap-xs mb-xs">
        {WEEKDAY_LABELS.map((label) => (
          <div key={label} className="text-label-sm text-on-surface-variant text-center">
            {label}
          </div>
        ))}
      </div>
      <div className="grid grid-cols-7 gap-xs">
        {weeks.flat().map((date) => {
          const iso = toIso(date)
          const inMonth = date.getMonth() === month
          const isToday = iso === todayIso
          const isSelected = iso === selectedDate
          const isBeforeMin = minDate && iso < minDate
          const info = dayStatus[iso]
          const dotColor = info ? statusColors[info.status] : null
          const accessibleLabel = `${date.toLocaleDateString(undefined, { weekday: 'long', month: 'long', day: 'numeric' })}${
            info?.status ? `, ${info.status.replace('_', ' ')}` : ''
          }`

          return (
            <button
              key={iso}
              type="button"
              disabled={!inMonth}
              onClick={() => onSelectDay?.(iso)}
              aria-label={accessibleLabel}
              aria-current={isToday ? 'date' : undefined}
              aria-pressed={isSelected}
              className={`
                relative h-12 rounded-md flex flex-col items-center justify-center gap-xs
                transition-colors
                ${!inMonth ? 'opacity-0 pointer-events-none' : ''}
                ${isSelected ? 'bg-primary text-on-primary' : 'hover:bg-surface-container'}
                ${isToday && !isSelected ? 'ring-2 ring-primary/40' : ''}
                ${isBeforeMin && !isSelected ? 'text-on-surface-variant/50' : 'text-on-surface'}
              `}
            >
              <span className="text-body-sm">{date.getDate()}</span>
              {dotColor ? (
                <span aria-hidden="true" className={`h-1.5 w-1.5 rounded-full ${isSelected ? 'bg-on-primary' : dotColor}`} />
              ) : null}
            </button>
          )
        })}
      </div>
    </div>
  )
}
