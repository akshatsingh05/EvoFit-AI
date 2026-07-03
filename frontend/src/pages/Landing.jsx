import { Link } from 'react-router-dom'
import Button from '../components/ui/Button.jsx'
import Card from '../components/ui/Card.jsx'

const FEATURES = [
  {
    title: 'AI-generated workouts',
    body: 'Every plan is built for your goals, equipment and experience — never a generic template.',
    accent: 'primary',
  },
  {
    title: 'Adaptive nutrition',
    body: 'Meal plans that respect your diet type and adjust as your calorie needs change.',
    accent: 'secondary',
  },
  {
    title: 'Daily check-ins',
    body: 'Log recovery and effort each day so your coaching actually responds to how you feel.',
    accent: 'tertiary',
  },
]

const ACCENT_BG = {
  primary: 'bg-primary/10 text-primary',
  secondary: 'bg-secondary/10 text-secondary',
  tertiary: 'bg-tertiary/10 text-tertiary',
}

export default function Landing() {
  return (
    <div className="min-h-screen bg-background">
      <nav className="px-container py-md flex items-center justify-between max-w-[1100px] mx-auto">
        <div className="flex items-center gap-sm">
          <span className="h-9 w-9 rounded-md bg-primary flex items-center justify-center">
            <span className="text-on-primary font-display font-bold text-body-md">E</span>
          </span>
          <span className="font-display font-bold text-headline-sm text-on-surface">EvoFit AI</span>
        </div>
        <div className="flex items-center gap-md">
          <Link to="/login" className="text-label-lg font-display text-on-surface-variant hover:text-on-surface">
            Log in
          </Link>
          <Link to="/signup">
            <Button variant="primary">Get started</Button>
          </Link>
        </div>
      </nav>

      <header className="px-container py-xxl max-w-[1100px] mx-auto text-center">
        <h1 className="text-display-lg-mobile md:text-display-lg text-on-surface max-w-[720px] mx-auto">
          Coaching that adapts to how your body actually responds
        </h1>
        <p className="mt-lg text-body-lg text-on-surface-variant max-w-[560px] mx-auto">
          EvoFit AI builds your workout and nutrition plan from your goals and medical history, then
          rewrites it every week based on your recovery, check-ins and progress.
        </p>
        <div className="mt-xl flex items-center justify-center gap-md">
          <Link to="/signup">
            <Button variant="primary" className="px-xl">
              Start your plan
            </Button>
          </Link>
          <Link to="/login">
            <Button variant="secondary" className="px-xl">
              I have an account
            </Button>
          </Link>
        </div>
      </header>

      <section className="px-container py-xxl max-w-[1100px] mx-auto">
        <div className="grid md:grid-cols-3 gap-lg">
          {FEATURES.map((f) => (
            <Card key={f.title}>
              <span className={`inline-flex h-10 w-10 items-center justify-center rounded-md mb-md ${ACCENT_BG[f.accent]}`}>
                ●
              </span>
              <h3 className="text-headline-sm text-on-surface mb-sm">{f.title}</h3>
              <p className="text-body-md text-on-surface-variant">{f.body}</p>
            </Card>
          ))}
        </div>
      </section>

      <footer className="px-container py-xl text-center text-body-sm text-on-surface-variant border-t border-divider">
        © {new Date().getFullYear()} EvoFit AI. Built as a capstone project.
      </footer>
    </div>
  )
}
