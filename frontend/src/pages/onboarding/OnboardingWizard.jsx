import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import GoalsStep from './GoalsStep.jsx'
import BodyMetricsStep from './BodyMetricsStep.jsx'
import FitnessExperienceStep from './FitnessExperienceStep.jsx'
import LifestyleDietStep from './LifestyleDietStep.jsx'
import MedicalHistoryStep from './MedicalHistoryStep.jsx'
import ReviewStep from './ReviewStep.jsx'
import * as onboardingService from '../../services/onboardingService'
import * as medicalHistoryService from '../../services/medicalHistoryService'
import { useAuth } from '../../hooks/useAuth.js'

const STEP_COUNT = 6

export default function OnboardingWizard() {
  const navigate = useNavigate()
  const { updateUser } = useAuth()
  const [stepIndex, setStepIndex] = useState(1)
  const [saving, setSaving] = useState(false)
  const [loaded, setLoaded] = useState(false)
  const [data, setData] = useState({
    goals: null,
    body_metrics: null,
    fitness_experience: null,
    lifestyle_diet: null,
    medical_history: null,
  })

  useEffect(() => {
    async function load() {
      try {
        const [onboarding, medicalHistory] = await Promise.all([
          onboardingService.getOnboarding(),
          medicalHistoryService.getMedicalHistory(),
        ])
        setData({
          goals: onboarding.goals,
          body_metrics: onboarding.body_metrics,
          fitness_experience: onboarding.fitness_experience,
          lifestyle_diet: onboarding.lifestyle_diet,
          medical_history: medicalHistory,
        })
        // Resume at the first incomplete step
        if (!onboarding.goals) setStepIndex(1)
        else if (!onboarding.body_metrics) setStepIndex(2)
        else if (!onboarding.fitness_experience) setStepIndex(3)
        else if (!onboarding.lifestyle_diet) setStepIndex(4)
        else if (!medicalHistory) setStepIndex(5)
        else setStepIndex(6)
      } finally {
        setLoaded(true)
      }
    }
    load()
  }, [])

  const goBack = () => setStepIndex((i) => Math.max(1, i - 1))

  const saveGoals = async (values) => {
    setSaving(true)
    try {
      await onboardingService.saveOnboardingStep({ goals: values })
      setData((d) => ({ ...d, goals: values }))
      setStepIndex(2)
    } finally {
      setSaving(false)
    }
  }

  const saveBodyMetrics = async (values) => {
    setSaving(true)
    try {
      await onboardingService.saveOnboardingStep({ body_metrics: values })
      setData((d) => ({ ...d, body_metrics: values }))
      setStepIndex(3)
    } finally {
      setSaving(false)
    }
  }

  const saveFitnessExperience = async (values) => {
    setSaving(true)
    try {
      await onboardingService.saveOnboardingStep({ fitness_experience: values })
      setData((d) => ({ ...d, fitness_experience: values }))
      setStepIndex(4)
    } finally {
      setSaving(false)
    }
  }

  const saveLifestyleDiet = async (values) => {
    setSaving(true)
    try {
      const result = await onboardingService.saveOnboardingStep({ lifestyle_diet: values })
      setData((d) => ({ ...d, lifestyle_diet: values }))
      if (result.is_complete) updateUser({ has_completed_onboarding: true })
      setStepIndex(5)
    } finally {
      setSaving(false)
    }
  }

  const saveMedicalHistory = async (values) => {
    setSaving(true)
    try {
      const result = await medicalHistoryService.saveMedicalHistory(values)
      setData((d) => ({ ...d, medical_history: result }))
      setStepIndex(6)
    } finally {
      setSaving(false)
    }
  }

  const finish = () => {
    navigate('/dashboard', { replace: true })
  }

  if (!loaded) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <span className="h-8 w-8 rounded-full border-2 border-primary border-t-transparent animate-spin" />
      </div>
    )
  }

  const commonProps = { stepIndex, stepCount: STEP_COUNT, onBack: goBack, saving }

  switch (stepIndex) {
    case 1:
      return <GoalsStep {...commonProps} defaultValues={data.goals} onNext={saveGoals} />
    case 2:
      return <BodyMetricsStep {...commonProps} defaultValues={data.body_metrics} onNext={saveBodyMetrics} />
    case 3:
      return <FitnessExperienceStep {...commonProps} defaultValues={data.fitness_experience} onNext={saveFitnessExperience} />
    case 4:
      return <LifestyleDietStep {...commonProps} defaultValues={data.lifestyle_diet} onNext={saveLifestyleDiet} />
    case 5:
      return <MedicalHistoryStep {...commonProps} defaultValues={data.medical_history} onNext={saveMedicalHistory} />
    case 6:
      return <ReviewStep {...commonProps} data={data} onNext={finish} />
    default:
      return null
  }
}
