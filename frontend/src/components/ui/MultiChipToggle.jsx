export default function MultiChipToggle({ options, selected, onToggle }) {
  return (
    <div className="flex flex-wrap gap-sm">
      {options.map((opt) => {
        const isSelected = selected.includes(opt.value)
        return (
          <button
            key={opt.value}
            type="button"
            onClick={() => onToggle(opt.value)}
            className={`
              px-md h-9 rounded-full text-label-md font-body transition-colors duration-150
              ${isSelected ? 'bg-primary text-on-primary' : 'bg-surface-container text-on-surface-variant hover:bg-surface-container-high'}
            `}
          >
            {opt.label}
          </button>
        )
      })}
    </div>
  )
}
