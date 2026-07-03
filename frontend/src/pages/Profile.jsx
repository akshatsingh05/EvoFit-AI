import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import AppLayout from '../layouts/AppLayout.jsx'
import Card from '../components/ui/Card.jsx'
import Input from '../components/ui/Input.jsx'
import Button from '../components/ui/Button.jsx'
import Chip from '../components/ui/Chip.jsx'
import * as profileService from '../services/profileService'
import { useAuth } from '../hooks/useAuth.js'

function InfoRow({ label, value }) {
  if (value === undefined || value === null || value === '') return null
  return (
    <div className="flex justify-between py-sm border-b border-divider last:border-none">
      <span className="text-body-sm text-on-surface-variant">{label}</span>
      <span className="text-body-sm text-on-surface font-medium text-right max-w-[60%]">
        {Array.isArray(value) ? (value.length ? value.join(', ') : '—') : String(value)}
      </span>
    </div>
  )
}

export default function Profile() {
  const { updateUser } = useAuth()
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [editing, setEditing] = useState(false)
  const [saveError, setSaveError] = useState('')

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm()

  useEffect(() => {
    async function load() {
      try {
        const data = await profileService.getProfile()
        setProfile(data)
        reset({ full_name: data.full_name })
      } catch {
        setError('Could not load your profile.')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [reset])

  const onSubmit = async (values) => {
    setSaveError('')
    try {
      const updated = await profileService.updateProfile({ fullName: values.full_name })
      setProfile(updated)
      updateUser({ full_name: updated.full_name })
      setEditing(false)
    } catch (err) {
      setSaveError(err.response?.data?.detail || 'Could not save changes.')
    }
  }

  if (loading) {
    return (
      <AppLayout title="Profile">
        <div className="flex justify-center py-xxl">
          <span className="h-8 w-8 rounded-full border-2 border-primary border-t-transparent animate-spin" />
        </div>
      </AppLayout>
    )
  }

  if (error || !profile) {
    return (
      <AppLayout title="Profile">
        <p className="text-body-md text-error">{error}</p>
      </AppLayout>
    )
  }

  return (
    <AppLayout title="Profile">
      <div className="space-y-lg">
        <Card>
          <div className="flex items-center justify-between mb-md">
            <h2 className="text-headline-sm text-on-surface">Personal information</h2>
            {!editing ? (
              <Button variant="ghost" className="h-9 px-md" onClick={() => setEditing(true)}>
                Edit
              </Button>
            ) : null}
          </div>

          {editing ? (
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-md">
              <Input
                label="Full name"
                error={errors.full_name?.message}
                {...register('full_name', { required: 'Full name is required', minLength: { value: 2, message: 'Too short' } })}
              />
              <Input label="Email" value={profile.email} disabled />
              {saveError ? <p className="text-body-sm text-error">{saveError}</p> : null}
              <div className="flex gap-sm">
                <Button type="submit" loading={isSubmitting}>Save changes</Button>
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => {
                    setEditing(false)
                    reset({ full_name: profile.full_name })
                  }}
                >
                  Cancel
                </Button>
              </div>
            </form>
          ) : (
            <>
              <InfoRow label="Full name" value={profile.full_name} />
              <InfoRow label="Email" value={profile.email} />
              <InfoRow label="Onboarding complete" value={profile.has_completed_onboarding ? 'Yes' : 'No'} />
            </>
          )}
        </Card>

        <Card>
          <h2 className="text-headline-sm text-on-surface mb-md">Goals</h2>
          <InfoRow label="Primary goal" value={profile.goals?.primary_goal} />
          <InfoRow label="Timeline (weeks)" value={profile.goals?.target_timeline_weeks} />
          <InfoRow label="Secondary goals" value={profile.goals?.secondary_goals} />
        </Card>

        <Card>
          <h2 className="text-headline-sm text-on-surface mb-md">Body metrics</h2>
          <InfoRow label="Height" value={profile.body_metrics?.height_cm ? `${profile.body_metrics.height_cm} cm` : null} />
          <InfoRow label="Weight" value={profile.body_metrics?.weight_kg ? `${profile.body_metrics.weight_kg} kg` : null} />
          <InfoRow label="Age" value={profile.body_metrics?.age} />
          <InfoRow label="Sex" value={profile.body_metrics?.sex} />
        </Card>

        <Card>
          <h2 className="text-headline-sm text-on-surface mb-md">Fitness experience</h2>
          <InfoRow label="Level" value={profile.fitness_experience?.experience_level} />
          <InfoRow label="Workouts / week" value={profile.fitness_experience?.workouts_per_week_current} />
          <InfoRow label="Equipment" value={profile.fitness_experience?.equipment_access} />
        </Card>

        <Card>
          <h2 className="text-headline-sm text-on-surface mb-md">Medical history</h2>
          {profile.medical_conditions.length === 0 && profile.medical_injuries.length === 0 && !profile.medications ? (
            <p className="text-body-sm text-on-surface-variant">No medical history recorded.</p>
          ) : (
            <>
              {profile.medical_conditions.length > 0 ? (
                <div className="mb-sm">
                  <span className="block text-body-sm text-on-surface-variant mb-xs">Conditions</span>
                  <div className="flex flex-wrap gap-xs">
                    {profile.medical_conditions.map((c) => (
                      <Chip key={c} color="tertiary">{c}</Chip>
                    ))}
                  </div>
                </div>
              ) : null}
              {profile.medical_injuries.length > 0 ? (
                <div className="mb-sm">
                  <span className="block text-body-sm text-on-surface-variant mb-xs">Injuries</span>
                  <div className="flex flex-wrap gap-xs">
                    {profile.medical_injuries.map((c) => (
                      <Chip key={c} color="secondary">{c}</Chip>
                    ))}
                  </div>
                </div>
              ) : null}
              <InfoRow label="Medications" value={profile.medications} />
              <InfoRow label="Allergies" value={profile.allergies} />
              <InfoRow label="Cleared for exercise" value={profile.cleared_for_exercise ? 'Yes' : 'No'} />
            </>
          )}
        </Card>
      </div>
    </AppLayout>
  )
}
