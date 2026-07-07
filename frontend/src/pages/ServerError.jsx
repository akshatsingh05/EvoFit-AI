import Button from '../components/ui/Button.jsx'

export default function ServerError({ onRetry }) {
  const handleRetry = () => {
    if (onRetry) {
      onRetry()
    } else {
      window.location.reload()
    }
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-background text-on-surface px-lg text-center gap-md">
      <p className="font-display text-display-md text-primary">500</p>
      <h1 className="font-display text-headline-md">Something went wrong</h1>
      <p className="text-body-lg text-on-surface-variant max-w-sm">
        We hit an unexpected error on our end. Please try again — if this keeps happening, refresh the page.
      </p>
      <div className="flex gap-sm mt-md">
        <Button variant="primary" onClick={handleRetry}>Try again</Button>
        <a href="/">
          <Button variant="secondary">Back to home</Button>
        </a>
      </div>
    </div>
  )
}
