import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import GoalsStep from './onboarding/GoalsStep.jsx'
import BodyMetricsStep from './onboarding/BodyMetricsStep.jsx'
import FitnessExperienceStep from './onboarding/FitnessExperienceStep.jsx'
import LifestyleDietStep from './onboarding/LifestyleDietStep.jsx'
import MedicalHistoryStep from './onboarding/MedicalHistoryStep.jsx'
import RegeneratePromptModal from '../components/shared/RegeneratePromptModal.jsx'
import { useSmartRegeneration } from '../hooks/useSmartRegeneration.js'
import * as onboardingService from '../services/onboardingService'
import * as medicalHistoryService from '../services/medicalHistoryService'
import { useToast } from '../context/ToastContext.jsx'

/**
 * Sprint 2: "The Profile page should essentially become an editable version
 * of the onboarding flow rather than introducing duplicate implementations."
 *
 * This route reuses the exact same Step components (and therefore the exact
 * same option lists, validation, and backend endpoints) the onboarding
 * wizard uses — the only difference is where `onNext` and `onBack` send you.
 */
const SECTION_CONFIG = {
  goals: { Component: GoalsStep, title: 'Goals' },
  'body-metrics': { Component: BodyMetricsStep, title: 'Body Metrics' },
  'fitness-experience': { Component: FitnessExperienceStep, title: 'Fitness Experience' },
  'lifestyle-diet': { Component: LifestyleDietStep, title: 'Lifestyle & Diet' },
  'medical-history': { Component: MedicalHistoryStep, title: 'Medical History' },
}

export default function ProfileEditSection() {
  const { section } = useParams()
  const navigate = useNavigate()
  const config = SECTION_CONFIG[section]

  const [defaultValues, setDefaultValues] = useState(null)
  const [loaded, setLoaded] = useState(false)
  const [saving, setSaving] = useState(false)
  const { showToast } = useToast()
  const { promptOpen, regenerating, promptIfChanged, regenerateNow, dismiss } = useSmartRegeneration()

  useEffect(() => {
    async function load() {
      try {
        if (section === 'medical-history') {
          const medical = await medicalHistoryService.getMedicalHistory()
          setDefaultValues(medical)
        } else {
          const onboarding = await onboardingService.getOnboarding()
          setDefaultValues(onboarding[section.replace('-', '_')])
        }
      } finally {
        setLoaded(true)
      }
    }
    if (config) load()
  }, [section])

  if (!config) {
    navigate('/profile', { replace: true })
    return null
  }

  const handleBack = () => navigate('/profile')

  const handleSave = async (values) => {
    setSaving(true)
    try {
      if (section === 'medical-history') {
        await medicalHistoryService.saveMedicalHistory(values)
      } else {
        await onboardingService.saveOnboardingStep({ [section.replace('-', '_')]: values })
      }
      const changed = promptIfChanged(defaultValues, values)
      setDefaultValues(values)
      if (!changed) {
        showToast(`${config.title} updated.`, 'success')
        navigate('/profile')
      }
    } catch {
      showToast(`Could not save ${config.title.toLowerCase()}. Please try again.`, 'error')
    } finally {
      setSaving(false)
    }
  }

  if (!loaded) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <span className="h-8 w-8 rounded-full border-2 border-primary border-t-transparent animate-spin" />
      </div>
    )
  }

  const { Component } = config

  return (
    <>
      <Component
        stepIndex={1}
        stepCount={1}
        defaultValues={defaultValues}
        onBack={handleBack}
        onNext={handleSave}
        saving={saving}
      />
      <RegeneratePromptModal
        open={promptOpen}
        regenerating={regenerating}
        onRegenerate={async () => {
          await regenerateNow()
          navigate('/profile')
        }}
        onLater={() => {
          dismiss()
          navigate('/profile')
        }}
      />
    </>
  )
}
