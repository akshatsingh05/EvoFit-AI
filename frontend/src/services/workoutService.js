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
