import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { Link } from 'react-router-dom'
import AppLayout from '../layouts/AppLayout.jsx'
import Card from '../components/ui/Card.jsx'
import Input from '../components/ui/Input.jsx'
import Button from '../components/ui/Button.jsx'
import Toggle from '../components/ui/Toggle.jsx'
import OptionCard from '../components/ui/OptionCard.jsx'
import * as settingsService from '../services/settingsService'
import { useAuth } from '../hooks/useAuth.js'

export default function Settings() {
  const { user, logout } = useAuth()
  const [settings, setSettings] = useState(null)
  const [loading, setLoading] = useState(true)
  const [savingPrefs, setSavingPrefs] = useState(false)
  const [prefsError, setPrefsError] = useState('')

  const [passwordError, setPasswordError] = useState('')
  const [passwordSuccess, setPasswordSuccess] = useState('')
  const {
    register,
    handleSubmit,
    reset: resetPasswordForm,
    watch,
    formState: { errors, isSubmitting },
  } = useForm()

  const newPassword = watch('new_password')

  useEffect(() => {
    async function load() {
      try {
        const data = await settingsService.getSettings()
        setSettings(data)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const patchSetting = async (patch) => {
    setSavingPrefs(true)
    setPrefsError('')
    const previous = settings
    setSettings((s) => ({ ...s, ...patch })) // optimistic update
    try {
      const updated = await settingsService.updateSettings(patch)
      setSettings(updated)
    } catch {
      setSettings(previous)
      setPrefsError('Could not save that change. Please try again.')
    } finally {
      setSavingPrefs(false)
    }
  }

  const onChangePassword = async (values) => {
    setPasswordError('')
    setPasswordSuccess('')
    try {
      await settingsService.changePassword({
        currentPassword: values.current_password,
        newPassword: values.new_password,
      })
      setPasswordSuccess('Password updated successfully.')
      resetPasswordForm()
    } catch (err) {
      setPasswordError(err.response?.data?.detail || 'Could not change password.')
    }
  }

  if (loading || !settings) {
    return (
      <AppLayout title="Settings">
        <div className="flex justify-center py-xxl">
          <span className="h-8 w-8 rounded-full border-2 border-primary border-t-transparent animate-spin" />
        </div>
      </AppLayout>
    )
  }

  return (
    <AppLayout title="Settings">
      <div className="space-y-lg">
        <Card>
          <h2 className="text-headline-sm text-on-surface mb-sm">Personal information</h2>
          <p className="text-body-sm text-on-surface-variant mb-md">
            Signed in as <span className="font-medium text-on-surface">{user?.email}</span>
          </p>
          <Link to="/profile">
            <Button variant="secondary" className="h-10 px-md">Edit profile</Button>
          </Link>
        </Card>

        <Card>
          <h2 className="text-headline-sm text-on-surface mb-sm">Theme</h2>
          <div className="grid grid-cols-2 gap-sm max-w-[320px]">
            <OptionCard
              label="Light"
              selected={settings.theme === 'light'}
              onSelect={() => patchSetting({ theme: 'light' })}
            />
            <OptionCard
              label="Dark"
              description="Coming soon"
              selected={settings.theme === 'dark'}
              onSelect={() => patchSetting({ theme: 'dark' })}
            />
          </div>
          <p className="text-body-sm text-on-surface-variant mt-sm">
            Your preference is saved now; dark mode styling itself ships in a later pass.
          </p>
        </Card>

        <Card>
          <h2 className="text-headline-sm text-on-surface mb-sm">Notifications</h2>
          {prefsError ? <p className="text-body-sm text-error mb-sm">{prefsError}</p> : null}
          <div className="divide-y divide-divider">
            <Toggle
              label="Email notifications"
              description="Plan updates and important account emails"
              checked={settings.email_notifications}
              onChange={(v) => patchSetting({ email_notifications: v })}
            />
            <Toggle
              label="Push notifications"
              description="Reminders for workouts and check-ins"
              checked={settings.push_notifications}
              onChange={(v) => patchSetting({ push_notifications: v })}
            />
            <Toggle
              label="Weekly summary email"
              description="A recap of your progress every week"
              checked={settings.weekly_summary_email}
              onChange={(v) => patchSetting({ weekly_summary_email: v })}
            />
          </div>
          {savingPrefs ? <p className="text-body-sm text-on-surface-variant mt-sm">Saving…</p> : null}
        </Card>

        <Card>
          <h2 className="text-headline-sm text-on-surface mb-md">Change password</h2>
          <form onSubmit={handleSubmit(onChangePassword)} className="space-y-md max-w-[420px]">
            <Input
              label="Current password"
              type="password"
              error={errors.current_password?.message}
              {...register('current_password', { required: 'Required' })}
            />
            <Input
              label="New password"
              type="password"
              error={errors.new_password?.message}
              {...register('new_password', {
                required: 'Required',
                minLength: { value: 8, message: 'Must be at least 8 characters' },
              })}
            />
            <Input
              label="Confirm new password"
              type="password"
              error={errors.confirm_password?.message}
              {...register('confirm_password', {
                required: 'Required',
                validate: (v) => v === newPassword || 'Passwords do not match',
              })}
            />
            {passwordError ? <p className="text-body-sm text-error">{passwordError}</p> : null}
            {passwordSuccess ? <p className="text-body-sm text-primary">{passwordSuccess}</p> : null}
            <Button type="submit" loading={isSubmitting}>Update password</Button>
          </form>
        </Card>

        <Card>
          <h2 className="text-headline-sm text-on-surface mb-sm">Log out</h2>
          <p className="text-body-sm text-on-surface-variant mb-md">You'll need to log in again to access your account.</p>
          <Button variant="secondary" onClick={logout}>Log out</Button>
        </Card>
      </div>
    </AppLayout>
  )
}
