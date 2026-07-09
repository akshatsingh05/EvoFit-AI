import api from './api'

export async function getNutritionPreferences() {
  const { data } = await api.get('/preferences/nutrition')
  return data
}

export async function updateNutritionPreferences(payload) {
  const { data } = await api.put('/preferences/nutrition', payload)
  return data
}

export async function getMealAlternatives({ offset = 0, dayIndex, mealType }) {
  const { data } = await api.get('/nutrition/week/meal-alternatives', {
    params: { offset, day_index: dayIndex, meal_type: mealType },
  })
  return data.alternatives
}

export async function replaceMeal({ offset = 0, dayIndex, mealType, replacementName = null }) {
  const { data } = await api.post('/nutrition/week/replace-meal', {
    offset,
    day_index: dayIndex,
    meal_type: mealType,
    replacement_name: replacementName,
  })
  return data
}
