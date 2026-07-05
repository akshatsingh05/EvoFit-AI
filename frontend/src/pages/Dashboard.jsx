import { useState, useEffect } from 'react'
import AppLayout from '../layouts/AppLayout.jsx'
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
        <div className="flex justify-center py-xxl">
          <span className="h-8 w-8 rounded-full border-2 border-primary border-t-transparent animate-spin" />
        </div>
      </AppLayout>
    )
  }

  if (error || !data) {
    return (
      <AppLayout title="Dashboard">
        <p className="text-body-md text-error">{error || 'Something went wrong.'}</p>
      </AppLayout>
    )
  }

  return (
    <AppLayout title="Dashboard">
      <WelcomeHeader fullName={data.full_name} />

      <div className="space-y-lg">
        <CheckInStatusBanner
          hasCheckedInToday={data.has_checked_in_today}
          unreadNotificationsCount={data.unread_notifications_count}
        />

        <AICoachTipCard tip={data.ai_coach_tip} />
        <AICoachRecommendations recommendations={data.ai_recommendations} />

        <div className="grid sm:grid-cols-2 gap-lg">
          <TodayWorkoutCard workout={data.today_workout} />
          <TodayNutritionCard nutrition={data.today_nutrition} />
        </div>

        <div className="grid sm:grid-cols-3 gap-lg">
          <RecoveryScoreCard score={data.recovery_score} />
          <WorkoutStreakCard days={data.workout_streak_days} />
          <FitnessScoreCard score={data.fitness_score} basis={data.fitness_score_basis} />
        </div>

        <WeeklyProgressChart points={data.weekly_progress} />

        <QuickActions actions={data.quick_actions_available} />
      </div>
    </AppLayout>
  )
}
