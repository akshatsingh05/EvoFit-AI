export function todayIso() {
  return new Date().toISOString().slice(0, 10)
}

export function addDays(isoDate, days) {
  const d = new Date(isoDate + 'T00:00:00')
  d.setDate(d.getDate() + days)
  return d.toISOString().slice(0, 10)
}

export function mondayOfWeek(isoDate) {
  const d = new Date(isoDate + 'T00:00:00')
  const day = (d.getDay() + 6) % 7
  d.setDate(d.getDate() - day)
  return d.toISOString().slice(0, 10)
}

export function weeksBetween(fromWeekStart, toWeekStart) {
  const from = new Date(fromWeekStart + 'T00:00:00')
  const to = new Date(toWeekStart + 'T00:00:00')
  return Math.round((to - from) / (7 * 24 * 60 * 60 * 1000))
}
