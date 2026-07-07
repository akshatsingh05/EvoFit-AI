import { lazy, Suspense } from 'react'
import { Routes, Route } from 'react-router-dom'
import Landing from './pages/Landing.jsx'
import Login from './pages/Login.jsx'
import Signup from './pages/Signup.jsx'
import ForgotPassword from './pages/ForgotPassword.jsx'
import NotFound from './pages/NotFound.jsx'
import ProtectedRoute from './routes/ProtectedRoute.jsx'

// Lazy-loaded: these pull in the bulk of the app's component code (charts,
// calendars, forms). Splitting them out keeps the initial bundle small for
// the logged-out Landing/Auth funnel, which loads eagerly above.
const OnboardingWizard = lazy(() => import('./pages/onboarding/OnboardingWizard.jsx'))
const Dashboard = lazy(() => import('./pages/Dashboard.jsx'))
const Profile = lazy(() => import('./pages/Profile.jsx'))
const ProfileEditSection = lazy(() => import('./pages/ProfileEditSection.jsx'))
const Settings = lazy(() => import('./pages/Settings.jsx'))
const Workout = lazy(() => import('./pages/Workout.jsx'))
const Nutrition = lazy(() => import('./pages/Nutrition.jsx'))
const Progress = lazy(() => import('./pages/Progress.jsx'))
const DailyCheckIn = lazy(() => import('./pages/DailyCheckIn.jsx'))

function RouteFallback() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background" role="status" aria-live="polite">
      <span className="sr-only">Loading…</span>
      <span className="h-8 w-8 rounded-full border-2 border-primary border-t-transparent animate-spin" aria-hidden="true" />
    </div>
  )
}

export default function App() {
  return (
    <Suspense fallback={<RouteFallback />}>
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />

        {/* Protected: onboarding itself doesn't require onboarding to be complete */}
        <Route element={<ProtectedRoute requireOnboarding={false} />}>
          <Route path="/onboarding" element={<OnboardingWizard />} />
        </Route>

        {/* Protected: everything else requires completed onboarding */}
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/profile/edit/:section" element={<ProfileEditSection />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/workout" element={<Workout />} />
          <Route path="/nutrition" element={<Nutrition />} />
          <Route path="/progress" element={<Progress />} />
          <Route path="/checkin" element={<DailyCheckIn />} />
        </Route>

        <Route path="*" element={<NotFound />} />
      </Routes>
    </Suspense>
  )
}
