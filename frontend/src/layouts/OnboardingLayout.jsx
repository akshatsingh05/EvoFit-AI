import ProgressBar from '../components/ui/ProgressBar.jsx'
import Button from '../components/ui/Button.jsx'

export default function OnboardingLayout({
  stepIndex,
  stepCount,
  stepLabel,
  title,
  subtitle,
  children,
  onBack,
  onNext,
  nextLabel = 'Continue',
  nextDisabled = false,
  nextLoading = false,
  showBack = true,
}) {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      <header className="px-container py-md border-b border-divider">
        <div className="max-w-[640px] mx-auto">
          <ProgressBar value={stepIndex} max={stepCount} label={stepLabel} />
        </div>
      </header>

      <main className="flex-1 flex items-start justify-center px-container py-xxl">
        <div className="w-full max-w-[640px]">
          <h1 className="text-headline-md text-on-surface mb-sm">{title}</h1>
          {subtitle ? <p className="text-body-md text-on-surface-variant mb-xl">{subtitle}</p> : null}
          {children}
        </div>
      </main>

      <footer className="sticky bottom-0 bg-surface-container-lowest border-t border-divider px-container py-md">
        <div className="max-w-[640px] mx-auto flex justify-between gap-md">
          {showBack ? (
            <Button variant="ghost" onClick={onBack}>
              Back
            </Button>
          ) : (
            <span />
          )}
          <Button onClick={onNext} disabled={nextDisabled} loading={nextLoading}>
            {nextLabel}
          </Button>
        </div>
      </footer>
    </div>
  )
}
