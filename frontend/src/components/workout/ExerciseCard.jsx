export default function ExerciseCard({ exercise, index }) {
  return (
    <div className="flex items-start gap-md py-md border-b border-divider last:border-none">
      <span className="h-8 w-8 rounded-full bg-primary/10 text-primary flex items-center justify-center text-label-md font-display shrink-0">
        {index + 1}
      </span>
      <div className="flex-1 min-w-0">
        <h4 className="text-label-lg font-display text-on-surface">{exercise.name}</h4>
        <div className="flex flex-wrap gap-md mt-xs text-body-sm text-on-surface-variant">
          <span>{exercise.sets} sets</span>
          <span>{exercise.reps} reps</span>
          <span>{exercise.rest_seconds}s rest</span>
        </div>
        <p className="text-body-sm text-on-surface-variant mt-xs">{exercise.instructions}</p>
      </div>
    </div>
  )
}
