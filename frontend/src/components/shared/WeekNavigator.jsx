import Button from '../ui/Button.jsx'

function formatWeekLabel(weekStartDate, offset) {
  if (offset === 0) return 'This week'
  const start = new Date(weekStartDate + 'T00:00:00')
  const end = new Date(start)
  end.setDate(end.getDate() + 6)
  const fmt = (d) => d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
  return `${fmt(start)} – ${fmt(end)}`
}

export default function WeekNavigator({ weekStartDate, offset, onOffsetChange }) {
  return (
    <div className="flex items-center gap-sm">
      <Button variant="ghost" className="h-9 w-9 px-0" onClick={() => onOffsetChange(offset - 1)} aria-label="Previous week">
        ‹
      </Button>
      <div className="min-w-[140px] text-center">
        <p className="text-label-md text-on-surface font-medium">{formatWeekLabel(weekStartDate, offset)}</p>
        {offset !== 0 ? (
          <button className="text-label-sm text-primary" onClick={() => onOffsetChange(0)}>
            Back to this week
          </button>
        ) : null}
      </div>
      <Button variant="ghost" className="h-9 w-9 px-0" onClick={() => onOffsetChange(offset + 1)} aria-label="Next week">
        ›
      </Button>
    </div>
  )
}
