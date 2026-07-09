import api from './api'

export async function getWorkoutPreferences() {
  const { data } = await api.get('/preferences/workout')
  return data
}

export async function updateWorkoutPreferences(payload) {
  const { data } = await api.put('/preferences/workout', payload)
  return data
}

export async function getExerciseAlternatives({ offset = 0, dayIndex, exerciseIndex }) {
  const { data } = await api.get('/workout/week/exercise-alternatives', {
    params: { offset, day_index: dayIndex, exercise_index: exerciseIndex },
  })
  return data.alternatives
}

export async function replaceExercise({ offset = 0, dayIndex, exerciseIndex, replacementName = null }) {
  const { data } = await api.post('/workout/week/replace-exercise', {
    offset,
    day_index: dayIndex,
    exercise_index: exerciseIndex,
    replacement_name: replacementName,
  })
  return data
}
