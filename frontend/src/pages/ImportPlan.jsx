import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { UploadCloud, FileText, History as HistoryIcon, Dumbbell, Salad } from 'lucide-react'
import AppLayout from '../layouts/AppLayout.jsx'
import Card from '../components/ui/Card.jsx'
import Button from '../components/ui/Button.jsx'
import Chip from '../components/ui/Chip.jsx'
import * as planImportService from '../services/planImportService'
import { getErrorMessage } from '../utils/errorMessage.js'

const ACCEPTED_EXTENSIONS = '.txt,.pdf,.docx,.png,.jpg,.jpeg'

function PlanTypeTabs({ planType, onChange }) {
  return (
    <div className="flex gap-sm mb-lg">
      <button
        type="button"
        onClick={() => onChange('workout')}
        className={`flex items-center gap-sm px-lg h-11 rounded-full text-label-md font-body transition-colors ${
          planType === 'workout' ? 'bg-primary text-on-primary' : 'bg-surface-container text-on-surface-variant'
        }`}
      >
        <Dumbbell size={16} /> Workout Plan
      </button>
      <button
        type="button"
        onClick={() => onChange('nutrition')}
        className={`flex items-center gap-sm px-lg h-11 rounded-full text-label-md font-body transition-colors ${
          planType === 'nutrition' ? 'bg-primary text-on-primary' : 'bg-surface-container text-on-surface-variant'
        }`}
      >
        <Salad size={16} /> Nutrition Plan
      </button>
    </div>
  )
}

function ImportForm({ planType, onImported }) {
  const [mode, setMode] = useState('manual')
  const [planName, setPlanName] = useState('')
  const [rawText, setRawText] = useState('')
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const placeholder =
    planType === 'workout'
      ? 'Monday\nBench Press 4x8\nIncline Bench 3x10\n\nTuesday\nDeadlift 3x5\nRows 4x8\n\nWednesday\nRest\n...'
      : 'Monday\nBreakfast\nOatmeal - 350 calories, 12g protein\nLunch\nGrilled Chicken and Quinoa Bowl\nWater: 2 liters\n...'

  const reset = () => {
    setPlanName('')
    setRawText('')
    setFile(null)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    if (!planName.trim()) {
      setError('Please give your plan a name.')
      return
    }
    if (mode === 'manual' && !rawText.trim()) {
      setError('Please paste your plan as text.')
      return
    }
    if (mode === 'file' && !file) {
      setError('Please choose a file to upload.')
      return
    }

    setLoading(true)
    try {
      const record =
        mode === 'manual'
          ? await planImportService.importPlanManual(planType, planName, rawText)
          : await planImportService.importPlanFile(planType, planName, file)
      reset()
      onImported(record)
    } catch (err) {
      setError(getErrorMessage(err, 'Could not import that plan. Please check the format and try again.'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card>
      <div className="flex gap-sm mb-lg">
        <button
          type="button"
          onClick={() => setMode('manual')}
          className={`px-md h-9 rounded-full text-label-sm font-body ${mode === 'manual' ? 'bg-primary/10 text-primary' : 'text-on-surface-variant'}`}
        >
          Paste text
        </button>
        <button
          type="button"
          onClick={() => setMode('file')}
          className={`px-md h-9 rounded-full text-label-sm font-body ${mode === 'file' ? 'bg-primary/10 text-primary' : 'text-on-surface-variant'}`}
        >
          Upload file
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-lg">
        <label className="block">
          <span className="block mb-sm font-body text-label-md text-on-surface-variant">Plan name</span>
          <input
            value={planName}
            onChange={(e) => setPlanName(e.target.value)}
            placeholder={planType === 'workout' ? 'e.g. My Push/Pull/Legs Split' : 'e.g. My Cutting Diet'}
            className="w-full h-[52px] px-md bg-input-fill rounded-md font-body text-body-md text-on-surface border-2 border-transparent focus:outline-none focus:border-primary focus:bg-surface-container-lowest transition-colors"
          />
        </label>

        {mode === 'manual' ? (
          <label className="block">
            <span className="block mb-sm font-body text-label-md text-on-surface-variant">Plan text</span>
            <textarea
              value={rawText}
              onChange={(e) => setRawText(e.target.value)}
              placeholder={placeholder}
              rows={12}
              className="w-full px-md py-md bg-input-fill rounded-md font-mono text-body-sm text-on-surface border-2 border-transparent focus:outline-none focus:border-primary focus:bg-surface-container-lowest transition-colors resize-y"
            />
          </label>
        ) : (
          <label className="flex flex-col items-center justify-center gap-sm border-2 border-dashed border-divider rounded-md py-2xl cursor-pointer hover:border-primary transition-colors">
            <UploadCloud size={28} className="text-on-surface-variant" aria-hidden="true" />
            <span className="text-label-md text-on-surface">
              {file ? file.name : 'Click to choose a file'}
            </span>
            <span className="text-body-sm text-on-surface-variant">TXT, PDF, DOCX, PNG, JPG, JPEG (max 15MB)</span>
            <input
              type="file"
              accept={ACCEPTED_EXTENSIONS}
              className="hidden"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
            />
          </label>
        )}

        {error ? <p className="text-body-sm text-error">{error}</p> : null}

        <Button type="submit" loading={loading} fullWidth>
          Import {planType === 'workout' ? 'Workout' : 'Nutrition'} Plan
        </Button>
      </form>
    </Card>
  )
}

function HistoryList({ planType }) {
  const [entries, setEntries] = useState([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const data = await planImportService.getImportHistory(planType)
      setEntries(data.entries)
    } finally {
      setLoading(false)
    }
  }, [planType])

  useEffect(() => {
    load()
  }, [load])

  if (loading) return <p className="text-body-sm text-on-surface-variant">Loading history…</p>
  if (entries.length === 0) {
    return <p className="text-body-sm text-on-surface-variant">No {planType} plans imported yet.</p>
  }

  const statusLabel = {
    none: 'Not applied', used_mine: 'Using imported plan', merged: 'Merged with EvoFit', used_evofit: 'Kept EvoFit plan',
  }

  return (
    <div className="space-y-sm">
      {entries.map((entry) => (
        <Card
          key={entry.id}
          padded={false}
          className="p-md flex items-center justify-between cursor-pointer hover:shadow-lg transition-shadow"
          onClick={() => navigate(`/import-plan/${entry.id}`)}
        >
          <div className="flex items-center gap-md min-w-0">
            <FileText size={18} className="text-on-surface-variant shrink-0" aria-hidden="true" />
            <div className="min-w-0">
              <p className="text-label-md text-on-surface truncate">{entry.plan_name}</p>
              <p className="text-body-sm text-on-surface-variant">
                {new Date(entry.created_at).toLocaleDateString()} · {entry.source_type}
              </p>
            </div>
          </div>
          <Chip color={entry.applied_status === 'none' ? 'neutral' : 'primary'}>
            {statusLabel[entry.applied_status] || entry.applied_status}
          </Chip>
        </Card>
      ))}
    </div>
  )
}

export default function ImportPlan() {
  const [planType, setPlanType] = useState('workout')
  const [tab, setTab] = useState('import')
  const navigate = useNavigate()

  return (
    <AppLayout title="Import Plan">
      <PlanTypeTabs planType={planType} onChange={setPlanType} />

      <div className="flex gap-sm mb-lg">
        <button
          type="button"
          onClick={() => setTab('import')}
          className={`flex items-center gap-sm px-md h-9 rounded-full text-label-sm font-body ${tab === 'import' ? 'bg-primary/10 text-primary' : 'text-on-surface-variant'}`}
        >
          <UploadCloud size={14} /> Import
        </button>
        <button
          type="button"
          onClick={() => setTab('history')}
          className={`flex items-center gap-sm px-md h-9 rounded-full text-label-sm font-body ${tab === 'history' ? 'bg-primary/10 text-primary' : 'text-on-surface-variant'}`}
        >
          <HistoryIcon size={14} /> History
        </button>
      </div>

      {tab === 'import' ? (
        <ImportForm
          key={planType}
          planType={planType}
          onImported={(record) => navigate(`/import-plan/${record.id}`)}
        />
      ) : (
        <HistoryList planType={planType} />
      )}
    </AppLayout>
  )
}
