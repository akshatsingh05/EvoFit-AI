import { useEffect, useState } from 'react'
import AppLayout from '../layouts/AppLayout.jsx'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import OptionCard from '../components/ui/OptionCard'
import Chip from '../components/ui/Chip'
import { getNutritionPreferences, updateNutritionPreferences } from '../services/nutritionPreferencesService'

const DIET_TYPES = [
  { value: 'vegetarian', label: 'Vegetarian' },
  { value: 'vegan', label: 'Vegan' },
  { value: 'eggetarian', label: 'Eggetarian' },
  { value: 'non_vegetarian', label: 'Non Vegetarian' },
]

const CUISINES = [
  { value: 'indian', label: 'Indian' },
  { value: 'mediterranean', label: 'Mediterranean' },
  { value: 'asian', label: 'Asian' },
  { value: 'western', label: 'Western' },
  { value: 'mixed', label: 'Mixed' },
]

const BUDGETS = [
  { value: 'low', label: 'Low' },
  { value: 'medium', label: 'Medium' },
  { value: 'high', label: 'High' },
]

const MEALS_PER_DAY = [3, 4, 5, 6]

const COOKING_TIME = [
  { value: 'quick', label: 'Quick Meals' },
  { value: 'moderate', label: 'Moderate' },
  { value: 'anything', label: 'Anything' },
]

function TagListEditor({ label, helperText, values, onChange, placeholder }) {
  const [draft, setDraft] = useState('')

  const addValue = () => {
    const trimmed = draft.trim()
    if (trimmed && !values.includes(trimmed)) {
      onChange([...values, trimmed])
    }
    setDraft('')
  }

  return (
    <div>
      <span className="block mb-sm font-body text-label-md text-on-surface-variant">{label}</span>
      {helperText ? <p className="text-body-sm text-on-surface-variant mb-sm">{helperText}</p> : null}
      <div className="flex flex-wrap gap-sm mb-sm">
        {values.map((v) => (
          <Chip key={v} onRemove={() => onChange(values.filter((x) => x !== v))}>
            {v}
          </Chip>
        ))}
      </div>
      <div className="flex gap-sm">
        <input
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              e.preventDefault()
              addValue()
            }
          }}
          placeholder={placeholder}
          className="flex-1 h-[48px] px-md bg-input-fill rounded-md font-body text-body-md text-on-surface border-2 border-transparent focus:outline-none focus:border-primary"
        />
        <Button variant="secondary" onClick={addValue}>Add</Button>
      </div>
    </div>
  )
}

export default function NutritionPreferences() {
  const [prefs, setPrefs] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    getNutritionPreferences()
      .then(setPrefs)
      .catch(() => setError('Could not load your nutrition preferences.'))
      .finally(() => setLoading(false))
  }, [])

  const update = (patch) => {
    setPrefs((prev) => ({ ...prev, ...patch }))
    setSaved(false)
  }

  const handleSave = async () => {
    setSaving(true)
    setError('')
    try {
      const updated = await updateNutritionPreferences(prefs)
      setPrefs(updated)
      setSaved(true)
    } catch {
      setError('Could not save your preferences. Please try again.')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <AppLayout title="Nutrition Preferences">
        <div className="flex justify-center py-xxl">
          <span className="h-8 w-8 rounded-full border-2 border-primary border-t-transparent animate-spin" />
        </div>
      </AppLayout>
    )
  }
  if (!prefs) {
    return (
      <AppLayout title="Nutrition Preferences">
        <p className="text-body-md text-error">{error || 'Something went wrong.'}</p>
      </AppLayout>
    )
  }

  return (
    <AppLayout title="Nutrition Preferences">
      <div className="space-y-lg">        <Card>
          <h3 className="font-display text-title-md text-on-surface mb-md">Diet Type</h3>
          <div className="grid grid-cols-2 gap-sm">
            {DIET_TYPES.map((d) => (
              <OptionCard
                key={d.value}
                label={d.label}
                selected={prefs.diet_type === d.value}
                onSelect={() => update({ diet_type: d.value })}
              />
            ))}
          </div>
        </Card>

        <Card>
          <h3 className="font-display text-title-md text-on-surface mb-md">Cuisine Preference</h3>
          <div className="grid grid-cols-2 gap-sm">
            {CUISINES.map((c) => (
              <OptionCard
                key={c.value}
                label={c.label}
                selected={prefs.cuisine_preference === c.value}
                onSelect={() => update({ cuisine_preference: c.value })}
              />
            ))}
          </div>
        </Card>

        <Card>
          <h3 className="font-display text-title-md text-on-surface mb-md">Budget</h3>
          <div className="grid grid-cols-3 gap-sm">
            {BUDGETS.map((b) => (
              <OptionCard
                key={b.value}
                label={b.label}
                selected={prefs.budget === b.value}
                onSelect={() => update({ budget: b.value })}
              />
            ))}
          </div>
        </Card>

        <Card>
          <h3 className="font-display text-title-md text-on-surface mb-md">Meals Per Day</h3>
          <div className="grid grid-cols-4 gap-sm">
            {MEALS_PER_DAY.map((m) => (
              <OptionCard
                key={m}
                label={String(m)}
                selected={prefs.meals_per_day === m}
                onSelect={() => update({ meals_per_day: m })}
              />
            ))}
          </div>
        </Card>

        <Card>
          <h3 className="font-display text-title-md text-on-surface mb-md">Cooking Time Preference</h3>
          <div className="grid grid-cols-3 gap-sm">
            {COOKING_TIME.map((c) => (
              <OptionCard
                key={c.value}
                label={c.label}
                selected={prefs.cooking_time_preference === c.value}
                onSelect={() => update({ cooking_time_preference: c.value })}
              />
            ))}
          </div>
        </Card>

        <Card>
          <span className="block mb-sm font-body text-label-md text-on-surface-variant">Water Goal (ml)</span>
          <input
            type="number"
            min={500}
            max={8000}
            step={100}
            value={prefs.water_goal_ml ?? ''}
            onChange={(e) => update({ water_goal_ml: e.target.value ? Number(e.target.value) : null })}
            placeholder="e.g. 3000"
            className="w-full h-[48px] px-md bg-input-fill rounded-md font-body text-body-md text-on-surface border-2 border-transparent focus:outline-none focus:border-primary"
          />
        </Card>

        <Card>
          <TagListEditor
            label="Favorite Foods"
            values={prefs.favorite_foods || []}
            onChange={(vals) => update({ favorite_foods: vals })}
            placeholder="e.g. Paneer Tikka"
          />
        </Card>

        <Card>
          <TagListEditor
            label="Foods You Dislike"
            values={prefs.disliked_foods || []}
            onChange={(vals) => update({ disliked_foods: vals })}
            placeholder="e.g. Overnight Oats"
          />
        </Card>

        <Card>
          <TagListEditor
            label="Preferred Snacks"
            values={prefs.preferred_snacks || []}
            onChange={(vals) => update({ preferred_snacks: vals })}
            placeholder="e.g. Roasted Chickpeas"
          />
        </Card>

        <Card>
          <TagListEditor
            label="Allergies"
            helperText="e.g. nuts, dairy, gluten, shellfish"
            values={prefs.allergies || []}
            onChange={(vals) => update({ allergies: vals })}
            placeholder="e.g. Peanuts"
          />
        </Card>

        {error ? <p className="text-body-sm text-error">{error}</p> : null}
        {saved ? <p className="text-body-sm text-secondary">Preferences saved.</p> : null}

        <Button fullWidth loading={saving} onClick={handleSave}>
          Save Nutrition Preferences
        </Button>
      </div>
    </AppLayout>
  )
}
