/**
 * Base shimmer block. Compose these into page-specific skeletons.
 * Uses a CSS-only shimmer (see index.css .skeleton-shimmer) so it stays
 * cheap even on low-powered devices.
 */
export function Skeleton({ className = '', rounded = 'rounded-md' }) {
  return (
    <div
      className={`skeleton-shimmer bg-surface-container-high ${rounded} ${className}`}
      aria-hidden="true"
    />
  )
}

export function SkeletonText({ lines = 1, className = '' }) {
  return (
    <div className={`space-y-sm ${className}`} aria-hidden="true">
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton
          key={i}
          className={`h-3 ${i === lines - 1 && lines > 1 ? 'w-2/3' : 'w-full'}`}
        />
      ))}
    </div>
  )
}

export function SkeletonCard({ className = '' }) {
  return (
    <div className={`bg-surface-container-lowest rounded-lg shadow-card p-lg ${className}`}>
      <div className="flex items-center gap-md mb-md">
        <Skeleton className="h-10 w-10" rounded="rounded-full" />
        <div className="flex-1 space-y-sm">
          <Skeleton className="h-3 w-1/3" />
          <Skeleton className="h-3 w-1/2" />
        </div>
      </div>
      <SkeletonText lines={2} />
    </div>
  )
}

export function SkeletonStatCard({ className = '' }) {
  return (
    <div className={`bg-surface-container-lowest rounded-lg shadow-card p-lg ${className}`}>
      <Skeleton className="h-3 w-2/5 mb-md" />
      <Skeleton className="h-8 w-1/3 mb-sm" />
      <Skeleton className="h-2 w-3/5" />
    </div>
  )
}

/** Full dashboard-shaped skeleton, used while the dashboard payload loads. */
export function DashboardSkeleton() {
  return (
    <div className="space-y-lg" role="status" aria-label="Loading dashboard">
      <div className="flex items-center gap-md">
        <Skeleton className="h-14 w-14" rounded="rounded-full" />
        <div className="space-y-sm flex-1">
          <Skeleton className="h-4 w-1/4" />
          <Skeleton className="h-3 w-1/3" />
        </div>
      </div>
      <SkeletonCard />
      <div className="grid sm:grid-cols-2 gap-lg">
        <SkeletonCard />
        <SkeletonCard />
      </div>
      <div className="grid sm:grid-cols-3 gap-lg">
        <SkeletonStatCard />
        <SkeletonStatCard />
        <SkeletonStatCard />
      </div>
      <SkeletonCard className="h-[220px]" />
      <span className="sr-only">Loading your dashboard…</span>
    </div>
  )
}

/** Generic list-shaped skeleton for history / import / report pages. */
export function ListSkeleton({ rows = 4 }) {
  return (
    <div className="space-y-md" role="status" aria-label="Loading">
      {Array.from({ length: rows }).map((_, i) => (
        <SkeletonCard key={i} />
      ))}
      <span className="sr-only">Loading…</span>
    </div>
  )
}
