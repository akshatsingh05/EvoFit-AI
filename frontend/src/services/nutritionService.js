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
