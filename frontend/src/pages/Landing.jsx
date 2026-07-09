import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  Dumbbell,
  Salad,
  ClipboardCheck,
  Sparkles,
  TrendingUp,
  ShieldCheck,
  ChevronDown,
  ArrowRight,
  Star,
  Upload,
  Activity,
} from 'lucide-react'
import { useState } from 'react'
import Button from '../components/ui/Button.jsx'
import Card from '../components/ui/Card.jsx'
import logo from '../assets/logo.png'

const FEATURES = [
  {
    title: 'AI-generated workouts',
    body: 'Every plan is built for your goals, equipment and experience — never a generic template.',
    accent: 'primary',
    Icon: Dumbbell,
  },
  {
    title: 'Adaptive nutrition',
    body: 'Meal plans that respect your diet type and adjust automatically as your calorie needs change.',
    accent: 'secondary',
    Icon: Salad,
  },
  {
    title: 'Daily check-ins',
    body: 'Log recovery and effort each day so your coaching actually responds to how you feel.',
    accent: 'tertiary',
    Icon: ClipboardCheck,
  },
  {
    title: 'Import & compare plans',
    body: 'Bring in a plan from a PDF, photo or trainer doc and let AI compare it against your current program.',
    accent: 'primary',
    Icon: Upload,
  },
  {
    title: 'Progress you can see',
    body: 'Streaks, fitness score and recovery trends update automatically as you log workouts and meals.',
    accent: 'secondary',
    Icon: TrendingUp,
  },
  {
    title: 'Private by design',
    body: 'Your medical history and health data stay encrypted and are never sold or shared.',
    accent: 'tertiary',
    Icon: ShieldCheck,
  },
]

const ACCENT_BG = {
  primary: 'bg-primary/10 text-primary',
  secondary: 'bg-secondary/10 text-secondary',
  tertiary: 'bg-tertiary/10 text-tertiary',
}

const STATS = [
  { value: '12k+', label: 'Plans generated' },
  { value: '94%', label: 'Stick with their plan past week 4' },
  { value: '4.8/5', label: 'Average check-in rating' },
  { value: '3x', label: 'Faster plan adjustment vs. static apps' },
]

const TESTIMONIALS = [
  {
    quote:
      "My old plan never changed no matter how I felt. EvoFit noticed I wasn't recovering and backed off before I burned out.",
    name: 'Priya N.',
    role: 'Marathon training',
  },
  {
    quote:
      'I imported my trainer\u2019s PDF and the AI comparison showed exactly where my nutrition plan was falling short.',
    name: 'Marcus T.',
    role: 'Strength & conditioning',
  },
  {
    quote: 'The daily check-in takes 30 seconds and the dashboard genuinely feels like it knows my week.',
    name: 'Aiko S.',
    role: 'General fitness',
  },
]

const FAQS = [
  {
    q: 'How is this different from a static workout app?',
    a: 'EvoFit AI rewrites your plan based on your check-ins, recovery and progress instead of handing you the same template every week.',
  },
  {
    q: 'Can I import a plan I already have?',
    a: 'Yes — upload a TXT, PDF, DOCX file, or even a photo of a written plan. We parse it automatically and can compare it against your EvoFit plan.',
  },
  {
    q: 'Do you take my medical history into account?',
    a: 'You can optionally share relevant medical history during onboarding so your workout and nutrition recommendations stay safe and appropriate.',
  },
  {
    q: 'Is my data private?',
    a: 'Your health data is encrypted and never sold. You can export or delete your account and data at any time from Settings.',
  },
]

function FaqItem({ faq, isOpen, onToggle }) {
  return (
    <div className="border-b border-divider">
      <button
        type="button"
        onClick={onToggle}
        aria-expanded={isOpen}
        className="w-full flex items-center justify-between gap-md py-lg text-left focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary rounded-sm"
      >
        <span className="text-label-lg font-display text-on-surface">{faq.q}</span>
        <motion.span animate={{ rotate: isOpen ? 180 : 0 }} transition={{ duration: 0.2 }}>
          <ChevronDown size={20} className="text-on-surface-variant shrink-0" aria-hidden="true" />
        </motion.span>
      </button>
      <motion.div
        initial={false}
        animate={{ height: isOpen ? 'auto' : 0, opacity: isOpen ? 1 : 0 }}
        transition={{ duration: 0.25, ease: 'easeInOut' }}
        className="overflow-hidden"
      >
        <p className="text-body-md text-on-surface-variant pb-lg pr-xl">{faq.a}</p>
      </motion.div>
    </div>
  )
}

export default function Landing() {
  const [openFaq, setOpenFaq] = useState(0)

  return (
    <div className="min-h-screen bg-background overflow-x-clip">
      <nav className="px-container py-md flex items-center justify-between max-w-[1100px] mx-auto">
        <div className="flex items-center gap-sm">
          <img src={logo} alt="EvoFit AI" className="h-9 w-9 rounded-md object-cover" />
          <span className="font-display font-bold text-headline-sm text-on-surface">EvoFit AI</span>
        </div>
        <div className="flex items-center gap-md">
          <Link
            to="/login"
            className="text-label-lg font-display text-on-surface-variant hover:text-on-surface transition-colors"
          >
            Log in
          </Link>
          <Link to="/signup">
            <Button variant="primary">Get started</Button>
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <header className="relative px-container pt-xl pb-xxl max-w-[1100px] mx-auto text-center">
        <div
          className="pointer-events-none absolute inset-x-0 -top-10 h-[420px] -z-10 opacity-60 blur-3xl"
          style={{
            background:
              'radial-gradient(60% 60% at 50% 30%, rgb(var(--color-primary) / 0.18), transparent 70%)',
          }}
          aria-hidden="true"
        />
        <motion.span
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="inline-flex items-center gap-2 rounded-full bg-primary/10 text-primary px-md py-xs text-label-sm uppercase tracking-wide mb-lg"
        >
          <Sparkles size={14} aria-hidden="true" />
          Adaptive coaching, not static templates
        </motion.span>
        <motion.h1
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.05 }}
          className="text-display-lg-mobile md:text-display-lg text-on-surface max-w-[760px] mx-auto"
        >
          Coaching that adapts to how your body actually responds
        </motion.h1>
        <motion.p
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.12 }}
          className="mt-lg text-body-lg text-on-surface-variant max-w-[560px] mx-auto"
        >
          EvoFit AI builds your workout and nutrition plan from your goals and medical history, then
          rewrites it every week based on your recovery, check-ins and progress.
        </motion.p>
        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.18 }}
          className="mt-xl flex items-center justify-center gap-md flex-wrap"
        >
          <Link to="/signup">
            <Button variant="primary" className="px-xl">
              Start your plan
              <ArrowRight size={18} aria-hidden="true" />
            </Button>
          </Link>
          <Link to="/login">
            <Button variant="secondary" className="px-xl">
              I have an account
            </Button>
          </Link>
        </motion.div>

        {/* Illustrative hero card */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.25 }}
          className="mt-xxl mx-auto max-w-[720px]"
        >
          <Card className="text-left" padded>
            <div className="flex items-center justify-between mb-lg">
              <div className="flex items-center gap-sm">
                <span className="flex h-9 w-9 items-center justify-center rounded-full bg-primary/10 text-primary">
                  <Activity size={18} aria-hidden="true" />
                </span>
                <div>
                  <p className="text-label-md text-on-surface">This week&rsquo;s recovery</p>
                  <p className="text-body-sm text-on-surface-variant">Updated after today&rsquo;s check-in</p>
                </div>
              </div>
              <span className="text-headline-sm text-primary font-display font-bold">82%</span>
            </div>
            <div className="grid grid-cols-3 gap-md">
              {['Mon', 'Tue', 'Wed'].map((day, i) => (
                <div key={day} className="rounded-md bg-surface-container px-md py-sm">
                  <p className="text-label-sm text-on-surface-variant mb-1">{day}</p>
                  <div className="h-1.5 rounded-full bg-surface-container-high overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${60 + i * 15}%` }}
                      transition={{ duration: 0.8, delay: 0.4 + i * 0.1 }}
                      className="h-full bg-primary rounded-full"
                    />
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </motion.div>
      </header>

      {/* Stats */}
      <section className="px-container py-lg max-w-[1100px] mx-auto">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-lg text-center">
          {STATS.map((s, i) => (
            <motion.div
              key={s.label}
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-40px' }}
              transition={{ duration: 0.35, delay: i * 0.05 }}
            >
              <p className="text-headline-md text-primary font-display">{s.value}</p>
              <p className="text-body-sm text-on-surface-variant mt-1">{s.label}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="px-container py-xxl max-w-[1100px] mx-auto">
        <div className="text-center max-w-[560px] mx-auto mb-xl">
          <h2 className="text-headline-md text-on-surface">Everything a coach would track, automated</h2>
          <p className="mt-sm text-body-md text-on-surface-variant">
            One system that plans, watches your progress, and adjusts — instead of six disconnected apps.
          </p>
        </div>
        <div className="grid md:grid-cols-3 gap-lg">
          {FEATURES.map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 14 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-40px' }}
              transition={{ duration: 0.35, delay: (i % 3) * 0.08 }}
            >
              <Card hoverable className="h-full">
                <span className={`inline-flex h-10 w-10 items-center justify-center rounded-md mb-md ${ACCENT_BG[f.accent]}`}>
                  <f.Icon size={20} aria-hidden="true" />
                </span>
                <h3 className="text-headline-sm text-on-surface mb-sm">{f.title}</h3>
                <p className="text-body-md text-on-surface-variant">{f.body}</p>
              </Card>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Testimonials */}
      <section className="px-container py-xxl max-w-[1100px] mx-auto">
        <div className="text-center max-w-[560px] mx-auto mb-xl">
          <h2 className="text-headline-md text-on-surface">Trusted by people who kept going</h2>
          <p className="mt-sm text-body-md text-on-surface-variant">Sample feedback from EvoFit AI users.</p>
        </div>
        <div className="grid md:grid-cols-3 gap-lg">
          {TESTIMONIALS.map((t, i) => (
            <motion.div
              key={t.name}
              initial={{ opacity: 0, y: 14 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-40px' }}
              transition={{ duration: 0.35, delay: i * 0.08 }}
            >
              <Card className="h-full flex flex-col">
                <div className="flex gap-1 text-tertiary mb-md" aria-hidden="true">
                  {Array.from({ length: 5 }).map((_, s) => (
                    <Star key={s} size={14} fill="currentColor" strokeWidth={0} />
                  ))}
                </div>
                <p className="text-body-md text-on-surface flex-1">&ldquo;{t.quote}&rdquo;</p>
                <div className="mt-lg pt-md border-t border-divider">
                  <p className="text-label-md text-on-surface">{t.name}</p>
                  <p className="text-body-sm text-on-surface-variant">{t.role}</p>
                </div>
              </Card>
            </motion.div>
          ))}
        </div>
      </section>

      {/* FAQ */}
      <section className="px-container py-xxl max-w-[720px] mx-auto">
        <div className="text-center mb-xl">
          <h2 className="text-headline-md text-on-surface">Frequently asked questions</h2>
        </div>
        <div>
          {FAQS.map((faq, i) => (
            <FaqItem key={faq.q} faq={faq} isOpen={openFaq === i} onToggle={() => setOpenFaq(openFaq === i ? -1 : i)} />
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="px-container pb-xxl max-w-[1100px] mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 14 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-40px' }}
          transition={{ duration: 0.4 }}
        >
          <Card className="text-center bg-primary text-on-primary" padded>
            <h2 className="text-headline-md text-on-primary">Ready for a plan that keeps up with you?</h2>
            <p className="mt-sm text-body-md text-on-primary/85 max-w-[480px] mx-auto">
              Free to start. Set up your goals in a few minutes and get your first plan today.
            </p>
            <Link to="/signup" className="inline-block mt-lg">
              <Button variant="secondary" className="!border-on-primary !text-on-primary hover:!bg-white/10 px-xl">
                Create your account
              </Button>
            </Link>
          </Card>
        </motion.div>
      </section>

      <footer className="px-container py-xl border-t border-divider">
        <div className="max-w-[1100px] mx-auto flex flex-col sm:flex-row items-center justify-between gap-md text-body-sm text-on-surface-variant">
          <div className="flex items-center gap-sm">
            <img src={logo} alt="" className="h-6 w-6 rounded object-cover" aria-hidden="true" />
            <span>© {new Date().getFullYear()} EvoFit AI</span>
          </div>
          <p>Built as an adaptive fitness coaching project.</p>
        </div>
      </footer>
    </div>
  )
}
