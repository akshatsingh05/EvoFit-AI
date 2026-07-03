import api from './api'

export async function getOnboarding() {
  const { data } = await api.get('/onboarding')
  return data
}

export async function saveOnboardingStep(stepPayload) {
  const { data } = await api.post('/onboarding', stepPayload)
  return data
}
