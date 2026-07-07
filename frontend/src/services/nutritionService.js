import api from './api'

export async function getNutritionPlan() {
  const { data } = await api.get('/nutrition')
  return data
}

export async function regenerateNutritionPlan() {
  const { data } = await api.post('/nutrition/regenerate')
  return data
}

export async function getMealCompletions() {
  const { data } = await api.get('/nutrition/completions')
  return data
}

export async function saveMealCompletion({ mealDate, mealType, status }) {
  const { data } = await api.post('/nutrition/completions', { meal_date: mealDate, meal_type: mealType, status })
  return data
}

// --- Sprint 2: week navigation ---

export async function getNutritionWeek(offset = 0) {
  const { data } = await api.get('/nutrition/week', { params: { offset } })
  return data
}

export async function regenerateNutritionWeek(offset = 0) {
  const { data } = await api.post('/nutrition/week/regenerate', null, { params: { offset } })
  return data
}

export async function getNutritionWeekCompletions(offset = 0) {
  const { data } = await api.get('/nutrition/completions/week', { params: { offset } })
  return data
}

export async function getNutritionHistory(limit = 12) {
  const { data } = await api.get('/nutrition/history', { params: { limit } })
  return data
}
