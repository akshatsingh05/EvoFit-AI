import { useEffect, useState } from 'react'
import AppLayout from '../layouts/AppLayout.jsx'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import OptionCard from '../components/ui/OptionCard'
import MultiChipToggle from '../components/ui/MultiChipToggle'
import Chip from '../components/ui/Chip'
import { getWorkoutPreferences, updateWorkoutPreferences } from '../services/workoutPreferencesService'

const STYLES = [
  { value: 'strength', label: 'Strength' },
  { value: 'hypertrophy', label: 'Hypertrophy' },
  { value: 'muscle_gain', label: 'Muscle Gain' },
  { value: 'fat_loss', label: 'Fat Loss' },
  { value: 'cardio', label: 'Cardio' },
  { value: 'functional_training', label: 'Functional Training' },
  { value: 'calisthenics', label: 'Calisthenics' },
  { value: 'powerlifting', label: 'Powerlifting' },
]

const LOCATIONS = [
  { value: 'gym', label: 'Gym' },
  { value: 'home', label: 'Home' },
  { value: 'mixed', label: 'Mixed' },
]

const EQUIPMENT = [
  { value: 'dumbbells', label: 'Dumbbells' },
  { value: 'barbell', label: 'Barbell' },
  { value: 'resistance_bands', label: 'Resistance Bands' },
  { value: 'machines', label: 'Machines' },
  { value: 'pull_up_bar', label: 'Pull-up Bar' },
  { value: 'bench', label: 'Bench' },
  { value: 'bodyweight_only', label: 'Bodyweight Only' },
]

const DURATIONS = [20, 30, 45, 60, 90]

const INTENSITIES = [
  { value: 'light', label: 'Light' },
  { value: 'moderate', label: 'Moderate' },
  { value: 'high', label: 'High' },
]

const TIMES = [
  { value: 'morning', label: 'Morning' },
  { value: 'afternoon', label: 'Afternoon' },
  { value: 'evening', label: 'Evening' },
]

const MUSCLE_GROUPS = [
  { value: 'chest', label: 'Chest' },
  { value: 'back', label: 'Back' },
  { value: 'legs', label: 'Legs' },
  { value: 'shoulders', label: 'Shoulders' },
  { value: 'arms', label: 'Arms' },
  { value: 'core', label: 'Core' },
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

export default function WorkoutPreferences() {
  const [prefs, setPrefs] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    getWorkoutPreferences()
      .then(setPrefs)
      .catch(() => setError('Could not load your workout preferences.'))
      .finally(() => setLoading(false))
  }, [])

  const update = (patch) => {
    setPrefs((prev) => ({ ...prev, ...patch }))
    setSaved(false)
  }

  const toggleInList = (field, value) => {
    const list = prefs[field] || []
    update({ [field]: list.includes(value) ? list.filter((v) => v !== value) : [...list, value] })
  }

  const handleSave = async () => {
    setSaving(true)
    setError('')
    try {
      const updated = await updateWorkoutPreferences(prefs)
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
      <AppLayout title="Workout Preferences">
        <div className="flex justify-center py-xxl">
          <span className="h-8 w-8 rounded-full border-2 border-primary border-t-transparent animate-spin" />
        </div>
      </AppLayout>
    )
  }
  if (!prefs) {
    return (
      <AppLayout title="Workout Preferences">
        <p className="text-body-md text-error">{error || 'Something went wrong.'}</p>
      </AppLayout>
    )
  }

  return (
    <AppLayout title="Workout Preferences">
      <div className="space-y-lg">        <Card>
          <h3 className="font-display text-title-md text-on-surface mb-md">Preferred Workout Style</h3>
          <div className="grid grid-cols-2 gap-sm">
            {STYLES.map((s) => (
              <OptionCard
                key={s.value}
                label={s.label}
                selected={prefs.workout_style === s.value}
                onSelect={() => update({ workout_style: s.value })}
              />
            ))}
          </div>
        </Card>

        <Card>
          <h3 className="font-display text-title-md text-on-surface mb-md">Preferred Workout Location</h3>
          <div className="grid grid-cols-3 gap-sm">
            {LOCATIONS.map((l) => (
              <OptionCard
                key={l.value}
                label={l.label}
                selected={prefs.workout_location === l.value}
                onSelect={() => update({ workout_location: l.value })}
              />
            ))}
          </div>
        </Card>

        <Card>
          <h3 className="font-display text-title-md text-on-surface mb-md">Equipment Available</h3>
          <MultiChipToggle
            options={EQUIPMENT}
            selected={prefs.equipment_available || []}
            onToggle={(v) => toggleInList('equipment_available', v)}
          />
        </Card>

        <Card>
          <h3 className="font-display text-title-md text-on-surface mb-md">Preferred Workout Duration</h3>
          <MultiChipToggle
            options={DURATIONS.map((d) => ({ value: d, label: `${d} min` }))}
            selected={prefs.preferred_duration_minutes ? [prefs.preferred_duration_minutes] : []}
            onToggle={(v) => update({ preferred_duration_minutes: v })}
          />
        </Card>

        <Card>
          <h3 className="font-display text-title-md text-on-surface mb-md">Workout Intensity</h3>
          <div className="grid grid-cols-3 gap-sm">
            {INTENSITIES.map((i) => (
              <OptionCard
                key={i.value}
                label={i.label}
                selected={prefs.workout_intensity === i.value}
                onSelect={() => update({ workout_intensity: i.value })}
              />
            ))}
          </div>
        </Card>

        <Card>
          <h3 className="font-display text-title-md text-on-surface mb-md">Preferred Workout Time</h3>
          <div className="grid grid-cols-3 gap-sm">
            {TIMES.map((t) => (
              <OptionCard
                key={t.value}
                label={t.label}
                selected={prefs.preferred_workout_time === t.value}
                onSelect={() => update({ preferred_workout_time: t.value })}
              />
            ))}
          </div>
        </Card>

        <Card>
          <h3 className="font-display text-title-md text-on-surface mb-md">Favorite Muscle Groups</h3>
          <MultiChipToggle
            options={MUSCLE_GROUPS}
            selected={prefs.favorite_muscle_groups || []}
            onToggle={(v) => toggleInList('favorite_muscle_groups', v)}
          />
        </Card>

        <Card>
          <TagListEditor
            label="Exercises You Like"
            helperText="These get prioritized in your generated workouts."
            values={prefs.liked_exercises || []}
            onChange={(vals) => update({ liked_exercises: vals })}
            placeholder="e.g. Push-Up"
          />
        </Card>

        <Card>
          <TagListEditor
            label="Exercises You Dislike"
            helperText="These will never be generated for you."
            values={prefs.disliked_exercises || []}
            onChange={(vals) => update({ disliked_exercises: vals })}
            placeholder="e.g. Burpees"
          />
        </Card>

        <Card>
          <TagListEditor
            label="Injuries / Movements To Avoid"
            helperText='Plain language works, e.g. "No overhead press", "Bad knees", "Shoulder pain".'
            values={prefs.avoid_movements || []}
            onChange={(vals) => update({ avoid_movements: vals })}
            placeholder="e.g. No overhead press"
          />
        </Card>

        {error ? <p className="text-body-sm text-error">{error}</p> : null}
        {saved ? <p className="text-body-sm text-secondary">Preferences saved.</p> : null}

        <Button fullWidth loading={saving} onClick={handleSave}>
          Save Workout Preferences
        </Button>
      </div>
    </AppLayout>
  )
}
