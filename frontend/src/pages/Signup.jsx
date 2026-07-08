import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link, useNavigate } from 'react-router-dom'
import AuthLayout from '../layouts/AuthLayout.jsx'
import Input from '../components/ui/Input.jsx'
import Button from '../components/ui/Button.jsx'
import { useAuth } from '../hooks/useAuth.js'
import { getErrorMessage } from '../utils/errorMessage.js'

export default function Signup() {
  const { signup } = useAuth()
  const navigate = useNavigate()
  const [serverError, setServerError] = useState('')
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
  } = useForm()

  const password = watch('password')

  const onSubmit = async (values) => {
    setServerError('')
    try {
      await signup({ fullName: values.fullName, email: values.email, password: values.password })
      navigate('/onboarding', { replace: true })
    } catch (err) {
      setServerError(getErrorMessage(err))
    }
  }

  return (
    <AuthLayout title="Create your account" subtitle="Takes about 2 minutes to get started.">
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-md">
        <Input
          label="Full name"
          placeholder="Jordan Lee"
          error={errors.fullName?.message}
          {...register('fullName', { required: 'Full name is required', minLength: { value: 2, message: 'Too short' } })}
        />
        <Input
          label="Email"
          type="email"
          placeholder="you@example.com"
          error={errors.email?.message}
          {...register('email', { required: 'Email is required' })}
        />
        <Input
          label="Password"
          type="password"
          placeholder="At least 8 characters"
          error={errors.password?.message}
          {...register('password', {
            required: 'Password is required',
            minLength: { value: 8, message: 'Must be at least 8 characters' },
            validate: (v) =>
              (/[A-Za-z]/.test(v) && /\d/.test(v)) || 'Must contain at least one letter and one number',
          })}
        />
        <Input
          label="Confirm password"
          type="password"
          placeholder="Re-enter your password"
          error={errors.confirmPassword?.message}
          {...register('confirmPassword', {
            required: 'Please confirm your password',
            validate: (value) => value === password || 'Passwords do not match',
          })}
        />

        {serverError ? <p className="text-body-sm text-error">{serverError}</p> : null}

        <Button type="submit" fullWidth loading={isSubmitting}>
          Create account
        </Button>
      </form>

      <p className="mt-lg text-center text-body-sm text-on-surface-variant">
        Already have an account?{' '}
        <Link to="/login" className="text-secondary font-medium">
          Log in
        </Link>
      </p>
    </AuthLayout>
  )
}
