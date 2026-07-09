import { useState, useEffect, useCallback } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import {
  ArrowLeft, Dumbbell, Salad, Droplet, Flame, TrendingUp, CheckCircle2,
  AlertTriangle, Download, Sparkles, Trash2,
} from 'lucide-react'
import AppLayout from '../layouts/AppLayout.jsx'
import Card from '../components/ui/Card.jsx'
import Button from '../components/ui/Button.jsx'
import Chip from '../components/ui/Chip.jsx'
import ProgressBar from '../components/ui/ProgressBar.jsx'
import * as planImportService from '../services/planImportService'
import { getErrorMessage } from '../utils/errorMessage.js'

function ScoreBadge({ label, score }) {
  const color = score >= 70 ? 'primary' : score >= 45 ? 'secondary' : 'tertiary'
  return (
    <div className="text-center">
      <div className={`mx-auto mb-xs h-16 w-16 rounded-full flex items-center justify-center text-title-md font-display font-bold ${
        color === 'primary' ? 'bg-primary/10 text-primary' : color === 'secondary' ? 'bg-secondary/10 text-secondary' : 'bg-tertiary/10 text-tertiary'
      }`}>
        {score}
      </div>
      <p className="text-body-sm text-on-surface-variant">{label}</p>
    </div>
  )
}

function MetricRow({ label, mine, evofit, unit = '' }) {
  return (
    <div className="grid grid-cols-3 items-center py-sm border-b border-divider last:border-0">
      <span className="text-body-sm text-on-surface-variant">{label}</span>
      <span className="text-label-md text-on-surface text-center">{mine}{unit}</span>
      <span className="text-label-md text-primary text-center">{evofit != null ? `${evofit}${unit}` : '—'}</span>
    </div>
  )
}

function WorkoutComparisonCard({ comparison }) {
  const { mine, evofit, muscle_groups: groups } = comparison
  return (
    <Card>
      <div className="flex items-center gap-sm mb-lg">
        <Dumbbell size={20} className="text-primary" aria-hidden="true" />
        <h3 className="text-title-md font-display font-bold text-on-surface">Workout Comparison</h3>
      </div>

      <div className="flex justify-around mb-lg">
        <ScoreBadge label="My Plan" score={mine.effectiveness_score} />
        {evofit ? <ScoreBadge label="EvoFit AI Plan" score={evofit.effectiveness_score} /> : null}
      </div>

      <div className="grid grid-cols-3 mb-sm text-label-sm text-on-surface-variant">
        <span>Metric</span>
        <span className="text-center">My Plan</span>
        <span className="text-center text-primary">EvoFit AI</span>
      </div>
      <MetricRow label="Training days/week" mine={mine.workout_days_count} evofit={evofit?.workout_days_count} />
      <MetricRow label="Total exercises" mine={mine.total_exercises} evofit={evofit?.total_exercises} />
      <MetricRow label="Detected split" mine={mine.detected_split} evofit={null} />
      <MetricRow label="Equipment" mine={mine.equipment_guess} evofit={evofit?.equipment_guess} />
      <MetricRow label="Muscle balance" mine={`${mine.muscle_balance_score}/100`} evofit={evofit ? `${evofit.muscle_balance_score}/100` : null} />
      <MetricRow
        label="Longest streak w/o rest"
        mine={`${mine.recovery.longest_consecutive_training_days}d`}
        evofit={evofit ? `${evofit.recovery.longest_consecutive_training_days}d` : null}
      />

      <div className="mt-lg">
        <p className="text-label-md text-on-surface mb-md">Muscle Volume (sets/week)</p>
        <div className="space-y-md">
          {groups.filter((g) => g !== 'cardio').map((group) => (
            <div key={group}>
              <div className="flex justify-between mb-xs">
                <span className="text-body-sm text-on-surface-variant capitalize">{group}</span>
                <span className="text-body-sm text-on-surface-variant">
                  {mine.muscle_volume[group]} {evofit ? `vs ${evofit.muscle_volume[group]}` : ''}
                </span>
              </div>
              <ProgressBar value={mine.muscle_volume[group]} max={Math.max(10, evofit?.muscle_volume[group] || 10, mine.muscle_volume[group])} />
            </div>
          ))}
        </div>
      </div>
    </Card>
  )
}

function NutritionComparisonCard({ comparison }) {
  const { mine, evofit } = comparison
  return (
    <Card>
      <div className="flex items-center gap-sm mb-lg">
        <Salad size={20} className="text-primary" aria-hidden="true" />
        <h3 className="text-title-md font-display font-bold text-on-surface">Nutrition Comparison</h3>
      </div>

      <div className="flex justify-around mb-lg">
        <ScoreBadge label="My Plan" score={mine.effectiveness_score} />
        {evofit ? <ScoreBadge label="EvoFit AI Plan" score={evofit.effectiveness_score} /> : null}
      </div>

      <div className="grid grid-cols-3 mb-sm text-label-sm text-on-surface-variant">
        <span>Metric</span>
        <span className="text-center">My Plan</span>
        <span className="text-center text-primary">EvoFit AI</span>
      </div>
      <MetricRow label="Calories/day" mine={mine.avg_daily_calories} evofit={evofit?.avg_daily_calories} unit=" kcal" />
      <MetricRow label="Protein/day" mine={mine.avg_daily_protein_g} evofit={evofit?.avg_daily_protein_g} unit="g" />
      <MetricRow label="Carbs/day" mine={mine.avg_daily_carbs_g} evofit={evofit?.avg_daily_carbs_g} unit="g" />
      <MetricRow label="Fat/day" mine={mine.avg_daily_fat_g} evofit={evofit?.avg_daily_fat_g} unit="g" />
      <MetricRow label="Water/day" mine={mine.avg_water_ml ?? '—'} evofit={evofit?.avg_water_ml} unit="ml" />
      <MetricRow label="Unique foods" mine={mine.unique_foods} evofit={evofit?.unique_foods} />
      <MetricRow label="Cuisine" mine={mine.cuisine_guess} evofit={null} />

      <div className="mt-lg flex items-center gap-sm text-body-sm text-on-surface-variant">
        <Droplet size={14} className="text-secondary" aria-hidden="true" />
        Hydration target: ~2000ml/day
      </div>
    </Card>
  )
}

function ObservationsCard({ observations }) {
  return (
    <Card>
      <div className="flex items-center gap-sm mb-md">
        <Sparkles size={20} className="text-tertiary" aria-hidden="true" />
        <h3 className="text-title-md font-display font-bold text-on-surface">AI Analysis</h3>
      </div>
      <ul className="space-y-sm">
        {observations.map((obs, i) => (
          <li key={i} className="flex gap-sm text-body-sm text-on-surface-variant">
            <AlertTriangle size={16} className="text-tertiary shrink-0 mt-[2px]" aria-hidden="true" />
            {obs}
          </li>
        ))}
      </ul>
    </Card>
  )
}

function SuggestionsCard({ suggestions }) {
  if (!suggestions.length) {
    return (
      <Card>
        <div className="flex items-center gap-sm">
          <CheckCircle2 size={20} className="text-primary" aria-hidden="true" />
          <p className="text-label-md text-on-surface">No changes needed — this plan looks solid.</p>
        </div>
      </Card>
    )
  }
  return (
    <Card>
      <div className="flex items-center gap-sm mb-md">
        <TrendingUp size={20} className="text-primary" aria-hidden="true" />
        <h3 className="text-title-md font-display font-bold text-on-surface">Suggestions</h3>
      </div>
      <div className="space-y-md">
        {suggestions.map((s, i) => (
          <div key={i} className="p-md rounded-md bg-surface-container">
            <div className="flex items-center gap-sm mb-xs">
              <Chip color="primary">{s.type}</Chip>
              <p className="text-label-md text-on-surface">{s.title}</p>
            </div>
            <p className="text-body-sm text-on-surface-variant">{s.detail}</p>
            <p className="text-body-sm text-on-surface-variant italic mt-xs">Why: {s.reason}</p>
          </div>
        ))}
      </div>
    </Card>
  )
}

function ApplyActions({ plan, onApply, applying }) {
  return (
    <Card>
      <h3 className="text-title-md font-display font-bold text-on-surface mb-md">Use this plan</h3>
      <p className="text-body-sm text-on-surface-variant mb-lg">
        Choose how EvoFit AI should use your imported {plan.plan_type} plan going forward.
      </p>
      <div className="flex flex-col gap-sm">
        <Button variant="primary" loading={applying === 'use_mine'} onClick={() => onApply('use_mine')}>
          Use My Plan
        </Button>
        <Button variant="secondary" loading={applying === 'merge'} onClick={() => onApply('merge')}>
          Merge My Plan with EvoFit
        </Button>
        <Button variant="ghost" loading={applying === 'use_evofit'} onClick={() => onApply('use_evofit')}>
          Use EvoFit Plan
        </Button>
      </div>
      {plan.applied_status !== 'none' ? (
        <p className="text-body-sm text-primary mt-md">Current status: {plan.applied_status.replace('_', ' ')}</p>
      ) : null}
    </Card>
  )
}

function ExportActions({ planId, planName }) {
  const [exporting, setExporting] = useState('')

  const handleExport = async (format) => {
    setExporting(format)
    try {
      await planImportService.exportReport(planId, planName, format)
    } finally {
      setExporting('')
    }
  }

  return (
    <Card>
      <h3 className="text-title-md font-display font-bold text-on-surface mb-md">Export Report</h3>
      <div className="flex gap-sm">
        <Button variant="secondary" loading={exporting === 'pdf'} onClick={() => handleExport('pdf')}>
          <Download size={16} /> PDF
        </Button>
        <Button variant="secondary" loading={exporting === 'docx'} onClick={() => handleExport('docx')}>
          <Download size={16} /> DOCX
        </Button>
      </div>
    </Card>
  )
}

export default function PlanComparison() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [plan, setPlan] = useState(null)
  const [analysis, setAnalysis] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [applying, setApplying] = useState('')
  const [applyResult, setApplyResult] = useState('')

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const [planData, analysisData] = await Promise.all([
        planImportService.getImportedPlan(id),
        planImportService.getAnalysis(id),
      ])
      setPlan(planData)
      setAnalysis(analysisData)
    } catch (err) {
      setError(getErrorMessage(err, 'Could not load this plan comparison.'))
    } finally {
      setLoading(false)
    }
  }, [id])

  useEffect(() => {
    load()
  }, [load])

  const handleApply = async (mode) => {
    setApplying(mode)
    setApplyResult('')
    try {
      await planImportService.applyDecision(id, mode)
      const updated = await planImportService.getImportedPlan(id)
      setPlan(updated)
      setApplyResult(
        mode === 'use_mine'
          ? 'Your imported plan is now your active EvoFit AI plan.'
          : mode === 'merge'
          ? 'Your imported plan has been merged into your EvoFit AI plan.'
          : 'Your EvoFit AI plan has been kept as-is.'
      )
    } catch (err) {
      setError(getErrorMessage(err, 'Could not apply that choice.'))
    } finally {
      setApplying('')
    }
  }

  const handleDelete = async () => {
    if (!window.confirm('Delete this imported plan and its comparison history?')) return
    await planImportService.deleteImportedPlan(id)
    navigate('/import-plan')
  }

  if (loading) {
    return (
      <AppLayout title="Plan Comparison">
        <p className="text-body-sm text-on-surface-variant">Loading comparison…</p>
      </AppLayout>
    )
  }

  if (error && !plan) {
    return (
      <AppLayout title="Plan Comparison">
        <p className="text-body-sm text-error">{error}</p>
        <Link to="/import-plan" className="text-primary text-label-md">Back to Import Plan</Link>
      </AppLayout>
    )
  }

  return (
    <AppLayout title={plan.plan_name}>
      <Link to="/import-plan" className="inline-flex items-center gap-sm text-body-sm text-on-surface-variant mb-lg hover:text-primary">
        <ArrowLeft size={16} /> Back to Import Plan
      </Link>

      {applyResult ? (
        <div className="mb-lg p-md rounded-md bg-primary/10 text-primary text-body-sm flex items-center gap-sm">
          <CheckCircle2 size={16} /> {applyResult}
        </div>
      ) : null}
      {error ? <p className="text-body-sm text-error mb-lg">{error}</p> : null}

      <div className="grid md:grid-cols-2 gap-lg mb-lg">
        {analysis && (plan.plan_type === 'workout'
          ? <WorkoutComparisonCard comparison={analysis.comparison} />
          : <NutritionComparisonCard comparison={analysis.comparison} />)}

        <div className="space-y-lg">
          <ObservationsCard observations={analysis.observations} />
          <SuggestionsCard suggestions={analysis.suggestions} />
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-lg mb-lg">
        <ApplyActions plan={plan} onApply={handleApply} applying={applying} />
        <ExportActions planId={plan.id} planName={plan.plan_name} />
      </div>

      <button
        type="button"
        onClick={handleDelete}
        className="inline-flex items-center gap-sm text-body-sm text-error hover:underline"
      >
        <Trash2 size={14} /> Delete this import
      </button>
    </AppLayout>
  )
}
