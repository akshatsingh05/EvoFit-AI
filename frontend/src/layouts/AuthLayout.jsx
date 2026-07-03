import { Link } from 'react-router-dom'

export default function AuthLayout({ children, title, subtitle }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-container py-xxl">
      <div className="w-full max-w-[420px]">
        <Link to="/" className="flex items-center gap-sm mb-xl justify-center">
          <span className="h-9 w-9 rounded-md bg-primary flex items-center justify-center">
            <span className="text-on-primary font-display font-bold text-body-md">E</span>
          </span>
          <span className="font-display font-bold text-headline-sm text-on-surface">EvoFit AI</span>
        </Link>

        <div className="text-center mb-xl">
          <h1 className="text-headline-md text-on-surface">{title}</h1>
          {subtitle ? <p className="mt-sm text-body-md text-on-surface-variant">{subtitle}</p> : null}
        </div>

        {children}
      </div>
    </div>
  )
}
