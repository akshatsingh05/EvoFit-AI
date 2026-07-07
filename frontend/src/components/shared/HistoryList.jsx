import Card from '../ui/Card.jsx'

/**
 * Renders a list of HistoryEntry objects (see backend schemas/history.py).
 * Domain-agnostic: Workout History and Nutrition History both use this as-is;
 * a future Daily Check-in / Recovery history can too.
 */
export default function HistoryList({ entries, onSelect, emptyMessage = 'No history yet.' }) {
  if (!entries || entries.length === 0) {
    return <p className="text-body-md text-on-surface-variant">{emptyMessage}</p>
  }

  return (
    <div className="space-y-sm">
      {entries.map((entry) => (
        <button
          key={entry.detail_ref}
          type="button"
          onClick={() => onSelect?.(entry.detail_ref)}
          className="w-full text-left"
        >
          <Card className="hover:bg-surface-container transition-colors" padded={true}>
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-label-lg font-display text-on-surface">{entry.title}</h4>
                <p className="text-body-sm text-on-surface-variant mt-xs">{entry.summary}</p>
              </div>
              <span className="text-label-sm text-primary">View →</span>
            </div>
          </Card>
        </button>
      ))}
    </div>
  )
}
