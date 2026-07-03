import { Routes, Route } from 'react-router-dom'
import Landing from './pages/Landing.jsx'
import Login from './pages/Login.jsx'
import Signup from './pages/Signup.jsx'
import ForgotPassword from './pages/ForgotPassword.jsx'
import OnboardingWizard from './pages/onboarding/OnboardingWizard.jsx'
import Dashboard from './pages/Dashboard.jsx'
import ProtectedRoute from './routes/ProtectedRoute.jsx'

export default function App() {
  return (
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
      </Route>

      <Route path="*" element={<Landing />} />
    </Routes>
  )
}
