import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import AuthLayout from '../layouts/AuthLayout.jsx'
import Input from '../components/ui/Input.jsx'
import Button from '../components/ui/Button.jsx'
import { useAuth } from '../hooks/useAuth.js'
import { getErrorMessage } from '../utils/errorMessage.js'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [serverError, setServerError] = useState('')
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm()

  const onSubmit = async (values) => {
    setServerError('')
    try {
      const user = await login(values)
      const redirectTo = location.state?.from?.pathname
      if (redirectTo) {
        navigate(redirectTo, { replace: true })
      } else {
        navigate(user.has_completed_onboarding ? '/dashboard' : '/onboarding', { replace: true })
      }
    } catch (err) {
      setServerError(getErrorMessage(err))
    }
  }

  return (
    <AuthLayout title="Welcome back" subtitle="Log in to see your latest plan and progress.">
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-md">
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
          placeholder="Enter your password"
          error={errors.password?.message}
          {...register('password', { required: 'Password is required' })}
        />

        {serverError ? <p className="text-body-sm text-error">{serverError}</p> : null}

        <div className="text-right">
          <Link to="/forgot-password" className="text-body-sm text-secondary">
            Forgot password?
          </Link>
        </div>

        <Button type="submit" fullWidth loading={isSubmitting}>
          Log in
        </Button>
      </form>

      <p className="mt-lg text-center text-body-sm text-on-surface-variant">
        Don&apos;t have an account?{' '}
        <Link to="/signup" className="text-secondary font-medium">
          Sign up
        </Link>
      </p>
    </AuthLayout>
  )
}
