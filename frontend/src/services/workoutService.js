import api from './api'

export async function getWorkoutPlan() {
  const { data } = await api.get('/workout')
  return data
}

export async function regenerateWorkoutPlan() {
  const { data } = await api.post('/workout/regenerate')
  return data
}

export async function getWorkoutCompletions() {
  const { data } = await api.get('/workout/completions')
  return data
}

export async function saveWorkoutCompletion({ workoutDate, status }) {
  const { data } = await api.post('/workout/completions', { workout_date: workoutDate, status })
  return data
}

// --- Sprint 2: week navigation ---

export async function getWorkoutWeek(offset = 0) {
  const { data } = await api.get('/workout/week', { params: { offset } })
  return data
}

export async function regenerateWorkoutWeek(offset = 0) {
  const { data } = await api.post('/workout/week/regenerate', null, { params: { offset } })
  return data
}

export async function getWorkoutWeekCompletions(offset = 0) {
  const { data } = await api.get('/workout/completions/week', { params: { offset } })
  return data
}

export async function getWorkoutHistory(limit = 12) {
  const { data } = await api.get('/workout/history', { params: { limit } })
  return data
}

export async function getWorkoutCalendar(start, end) {
  const { data } = await api.get('/workout/calendar', { params: { start, end } })
  return data
}
