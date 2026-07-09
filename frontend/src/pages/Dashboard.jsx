import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { AlertTriangle } from 'lucide-react'
import AppLayout from '../layouts/AppLayout.jsx'
import { DashboardSkeleton } from '../components/ui/Skeleton.jsx'
import { staggerContainer, staggerItem } from '../components/ui/PageTransition.jsx'
import Button from '../components/ui/Button.jsx'
import WelcomeHeader from '../components/dashboard/WelcomeHeader.jsx'
import CheckInStatusBanner from '../components/dashboard/CheckInStatusBanner.jsx'
import TodayWorkoutCard from '../components/dashboard/TodayWorkoutCard.jsx'
import TodayNutritionCard from '../components/dashboard/TodayNutritionCard.jsx'
import RecoveryScoreCard from '../components/dashboard/RecoveryScoreCard.jsx'
import WorkoutStreakCard from '../components/dashboard/WorkoutStreakCard.jsx'
import FitnessScoreCard from '../components/dashboard/FitnessScoreCard.jsx'
import WeeklyProgressChart from '../components/dashboard/WeeklyProgressChart.jsx'
import AICoachTipCard from '../components/dashboard/AICoachTipCard.jsx'
import AICoachRecommendations from '../components/dashboard/AICoachRecommendations.jsx'
import QuickActions from '../components/dashboard/QuickActions.jsx'
import * as dashboardService from '../services/dashboardService'

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    async function load() {
      try {
        const result = await dashboardService.getDashboard()
        if (!cancelled) setData(result)
      } catch {
        if (!cancelled) setError('Could not load your dashboard. Please try again.')
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    load()
    return () => {
      cancelled = true
    }
  }, [])

  if (loading) {
    return (
      <AppLayout title="Dashboard">
        <DashboardSkeleton />
      </AppLayout>
    )
  }

  if (error || !data) {
    return (
      <AppLayout title="Dashboard">
        <div className="flex flex-col items-center text-center py-xxl px-lg">
          <span className="flex h-14 w-14 items-center justify-center rounded-full bg-error/10 text-error mb-lg">
            <AlertTriangle size={26} aria-hidden="true" />
          </span>
          <h3 className="text-headline-sm text-on-surface mb-sm">Couldn&rsquo;t load your dashboard</h3>
          <p className="text-body-md text-on-surface-variant max-w-[360px] mb-lg">
            {error || 'Something went wrong while loading your data.'}
          </p>
          <Button variant="primary" onClick={() => window.location.reload()}>
            Try again
          </Button>
        </div>
      </AppLayout>
    )
  }

  return (
    <AppLayout title="Dashboard">
      <WelcomeHeader fullName={data.full_name} />

      <motion.div
        className="space-y-lg"
        variants={staggerContainer}
        initial="initial"
        animate="animate"
      >
        <motion.div variants={staggerItem}>
          <CheckInStatusBanner
            hasCheckedInToday={data.has_checked_in_today}
            unreadNotificationsCount={data.unread_notifications_count}
          />
        </motion.div>

        <motion.div variants={staggerItem}>
          <AICoachTipCard tip={data.ai_coach_tip} />
        </motion.div>
        <motion.div variants={staggerItem}>
          <AICoachRecommendations recommendations={data.ai_recommendations} />
        </motion.div>

        <motion.div variants={staggerItem} className="grid sm:grid-cols-2 gap-lg">
          <TodayWorkoutCard workout={data.today_workout} />
          <TodayNutritionCard nutrition={data.today_nutrition} />
        </motion.div>

        <motion.div variants={staggerItem} className="grid sm:grid-cols-3 gap-lg">
          <RecoveryScoreCard score={data.recovery_score} />
          <WorkoutStreakCard days={data.workout_streak_days} />
          <FitnessScoreCard score={data.fitness_score} basis={data.fitness_score_basis} />
        </motion.div>

        <motion.div variants={staggerItem}>
          <WeeklyProgressChart points={data.weekly_progress} />
        </motion.div>

        <motion.div variants={staggerItem}>
          <QuickActions actions={data.quick_actions_available} />
        </motion.div>
      </motion.div>
    </AppLayout>
  )
}
