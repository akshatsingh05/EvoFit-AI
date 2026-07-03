import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link } from 'react-router-dom'
import AuthLayout from '../layouts/AuthLayout.jsx'
import Input from '../components/ui/Input.jsx'
import Button from '../components/ui/Button.jsx'
import * as authService from '../services/authService'

export default function ForgotPassword() {
  const [sent, setSent] = useState(false)
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm()

  const onSubmit = async (values) => {
    await authService.forgotPassword(values.email)
    setSent(true)
  }

  if (sent) {
    return (
      <AuthLayout title="Check your email" subtitle="If an account exists for that address, we've sent a reset link.">
        <Link to="/login">
          <Button fullWidth variant="secondary">
            Back to log in
          </Button>
        </Link>
      </AuthLayout>
    )
  }

  return (
    <AuthLayout title="Reset your password" subtitle="Enter your email and we'll send you a reset link.">
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-md">
        <Input
          label="Email"
          type="email"
          placeholder="you@example.com"
          error={errors.email?.message}
          {...register('email', { required: 'Email is required' })}
        />
        <Button type="submit" fullWidth loading={isSubmitting}>
          Send reset link
        </Button>
      </form>
      <p className="mt-lg text-center text-body-sm text-on-surface-variant">
        <Link to="/login" className="text-secondary font-medium">
          Back to log in
        </Link>
      </p>
    </AuthLayout>
  )
}
