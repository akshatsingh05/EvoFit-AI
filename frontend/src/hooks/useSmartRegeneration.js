import { useState } from 'react'
import * as workoutService from '../services/workoutService'
import * as nutritionService from '../services/nutritionService'

/**
 * Shared logic for the Smart Regeneration Prompt (Sprint 2 requirement #7).
 * Any screen that saves a profile section affecting AI plans can call
 * `promptIfChanged(before, after)` and this hook takes care of showing the
 * modal and regenerating both plans if the user confirms.
 */
export function useSmartRegeneration() {
  const [open, setOpen] = useState(false)
  const [regenerating, setRegenerating] = useState(false)

  const promptIfChanged = (before, after) => {
    const changed = JSON.stringify(before || null) !== JSON.stringify(after || null)
    if (changed) setOpen(true)
    return changed
  }

  const regenerateNow = async () => {
    setRegenerating(true)
    try {
      await Promise.all([workoutService.regenerateWorkoutPlan(), nutritionService.regenerateNutritionPlan()])
    } finally {
      setRegenerating(false)
      setOpen(false)
    }
  }

  const dismiss = () => setOpen(false)

  return { promptOpen: open, regenerating, promptIfChanged, regenerateNow, dismiss }
}
