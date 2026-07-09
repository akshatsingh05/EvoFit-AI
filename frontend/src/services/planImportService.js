import api from './api'

// --- Feature 1 & 2: import ---

export async function importPlanManual(planType, planName, rawText) {
  const { data } = await api.post(`/plan-import/${planType}/manual`, {
    plan_name: planName,
    raw_text: rawText,
  })
  return data
}

export async function importPlanFile(planType, planName, file) {
  const formData = new FormData()
  formData.append('plan_name', planName)
  formData.append('file', file)
  const { data } = await api.post(`/plan-import/${planType}/file`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

// --- Feature 7: history ---

export async function getImportHistory(planType) {
  const { data } = await api.get('/plan-import/history', { params: planType ? { plan_type: planType } : {} })
  return data
}

export async function getImportedPlan(importedPlanId) {
  const { data } = await api.get(`/plan-import/${importedPlanId}`)
  return data
}

export async function deleteImportedPlan(importedPlanId) {
  const { data } = await api.delete(`/plan-import/${importedPlanId}`)
  return data
}

// --- Feature 3/4/5: compare + AI analysis + suggestions ---

export async function comparePlan(importedPlanId) {
  const { data } = await api.post(`/plan-import/${importedPlanId}/compare`)
  return data
}

export async function getAnalysis(importedPlanId) {
  const { data } = await api.get(`/plan-import/${importedPlanId}/analysis`)
  return data
}

// --- Feature 6: apply decision ---

export async function applyDecision(importedPlanId, mode) {
  const { data } = await api.post(`/plan-import/${importedPlanId}/apply`, { mode })
  return data
}

// --- Feature 8: export ---

export function exportReportUrl(importedPlanId, format) {
  return `/plan-import/${importedPlanId}/export?format=${format}`
}

async function downloadBlob(url, filename) {
  const { data } = await api.get(url, { responseType: 'blob' })
  const blobUrl = window.URL.createObjectURL(new Blob([data]))
  const link = document.createElement('a')
  link.href = blobUrl
  link.setAttribute('download', filename)
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(blobUrl)
}

export async function exportReport(importedPlanId, planName, format) {
  const ext = format === 'docx' ? 'docx' : 'pdf'
  await downloadBlob(exportReportUrl(importedPlanId, format), `${planName.replace(/\s+/g, '_')}_report.${ext}`)
}

export async function exportCombinedReport(format) {
  const ext = format === 'docx' ? 'docx' : 'pdf'
  await downloadBlob(`/plan-import/export/combined?format=${format}`, `EvoFit_Combined_Report.${ext}`)
}
