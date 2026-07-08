import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { Link, useNavigate } from 'react-router-dom'
import AppLayout from '../layouts/AppLayout.jsx'
import Card from '../components/ui/Card.jsx'
import Input from '../components/ui/Input.jsx'
import Button from '../components/ui/Button.jsx'
import Toggle from '../components/ui/Toggle.jsx'
import OptionCard from '../components/ui/OptionCard.jsx'
import * as settingsService from '../services/settingsService'
import * as profileService from '../services/profileService'
import { useAuth } from '../hooks/useAuth.js'
import { useTheme } from '../context/ThemeContext.jsx'
import { useToast } from '../context/ToastContext.jsx'
import { getErrorMessage } from '../utils/errorMessage.js'

export default function Settings() {
  const { user, logout } = useAuth()
  const { theme, setTheme, syncFromUserSettings } = useTheme()
  const { showToast } = useToast()
  const navigate = useNavigate()
  const [settings, setSettings] = useState(null)
  const [loading, setLoading] = useState(true)
  const [savingPrefs, setSavingPrefs] = useState(false)
  const [prefsError, setPrefsError] = useState('')

  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [deleteConfirmText, setDeleteConfirmText] = useState('')
  const [deleting, setDeleting] = useState(false)
  const [deleteError, setDeleteError] = useState('')

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
        syncFromUserSettings(data.theme)
      } finally {
        setLoading(false)
      }
    }
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
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
      showToast('Could not save that change.', 'error')
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
      showToast('Password updated.', 'success')
    } catch (err) {
      const message = getErrorMessage(err, 'Could not change password.')
      setPasswordError(message)
      showToast(message, 'error')
    }
  }

  const handleDeleteAccount = async () => {
    setDeleting(true)
    setDeleteError('')
    try {
      await profileService.deleteAccount()
      logout()
      navigate('/', { replace: true })
    } catch (err) {
      setDeleteError(getErrorMessage(err, 'Could not delete your account. Please try again.'))
      showToast('Could not delete your account.', 'error')
      setDeleting(false)
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
              selected={theme === 'light'}
              onSelect={() => {
                setTheme('light')
                patchSetting({ theme: 'light' })
              }}
            />
            <OptionCard
              label="Dark"
              selected={theme === 'dark'}
              onSelect={() => {
                setTheme('dark')
                patchSetting({ theme: 'dark' })
              }}
            />
          </div>
          <p className="text-body-sm text-on-surface-variant mt-sm">
            Applies instantly and stays set across refreshes, logout, and other devices.
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
                validate: (v) =>
                  (/[A-Za-z]/.test(v) && /\d/.test(v)) || 'Must contain at least one letter and one number',
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

        <Card className="border-2 border-error">
          <h2 className="text-headline-sm text-error mb-sm">Danger zone</h2>
          <p className="text-body-sm text-on-surface-variant mb-md">
            Deleting your account permanently removes your profile, medical history, workout and nutrition plans,
            progress history, notifications, and check-ins. This cannot be undone.
          </p>

          {!showDeleteConfirm ? (
            <Button variant="secondary" className="border-error text-error" onClick={() => setShowDeleteConfirm(true)}>
              Delete account
            </Button>
          ) : (
            <div className="space-y-md max-w-[420px]">
              <p className="text-body-sm text-on-surface">
                Type <span className="font-medium">DELETE</span> to confirm you want to permanently delete your account.
              </p>
              <Input
                value={deleteConfirmText}
                onChange={(e) => setDeleteConfirmText(e.target.value)}
                placeholder="DELETE"
              />
              {deleteError ? <p className="text-body-sm text-error">{deleteError}</p> : null}
              <div className="flex gap-sm">
                <Button
                  variant="primary"
                  className="bg-error hover:bg-error"
                  disabled={deleteConfirmText !== 'DELETE'}
                  loading={deleting}
                  onClick={handleDeleteAccount}
                >
                  Permanently delete my account
                </Button>
                <Button
                  variant="ghost"
                  onClick={() => {
                    setShowDeleteConfirm(false)
                    setDeleteConfirmText('')
                    setDeleteError('')
                  }}
                >
                  Cancel
                </Button>
              </div>
            </div>
          )}
        </Card>
      </div>
    </AppLayout>
  )
}
