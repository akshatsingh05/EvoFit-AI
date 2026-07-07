import { Link } from 'react-router-dom'
import Button from '../components/ui/Button.jsx'

export default function NotFound() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-background text-on-surface px-lg text-center gap-md">
      <p className="font-display text-display-md text-primary">404</p>
      <h1 className="font-display text-headline-md">Page not found</h1>
      <p className="text-body-lg text-on-surface-variant max-w-sm">
        The page you're looking for doesn't exist or may have moved.
      </p>
      <Link to="/" className="mt-md">
        <Button variant="primary">Back to home</Button>
      </Link>
    </div>
  )
}
