export default function WeekScheduleTabs({ schedule, selectedIndex, onSelect, completions }) {
  return (
    <div className="flex gap-xs overflow-x-auto pb-xs">
      {schedule.map((day, i) => {
        const isSelected = i === selectedIndex
        const status = completions[day.date]
        return (
          <button
            key={day.day_name}
            onClick={() => onSelect(i)}
            className={`
              flex flex-col items-center justify-center h-16 w-14 rounded-md shrink-0 transition-colors
              ${isSelected ? 'bg-primary text-on-primary' : 'bg-surface-container text-on-surface-variant hover:bg-surface-container-high'}
            `}
          >
            <span className="text-label-sm">{day.day_name.slice(0, 3)}</span>
            <span className="text-body-sm mt-xs">
              {day.is_rest_day ? '—' : status === 'completed' ? '✓' : status === 'skipped' ? '×' : '•'}
            </span>
          </button>
        )
      })}
    </div>
  )
}
