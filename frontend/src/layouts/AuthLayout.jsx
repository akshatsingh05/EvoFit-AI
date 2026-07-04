import { Link } from 'react-router-dom'
import logo from '../assets/logo.png'

export default function AuthLayout({ children, title, subtitle }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-container py-xxl">
      <div className="w-full max-w-[420px]">
        <Link to="/" className="flex items-center gap-sm mb-xl justify-center">
          <img src={logo} alt="EvoFit AI" className="h-9 w-9 rounded-md object-cover" />
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
