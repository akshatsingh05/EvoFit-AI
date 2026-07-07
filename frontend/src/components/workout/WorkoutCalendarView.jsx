import { useState, useEffect, useMemo } from 'react'
import Calendar from '../shared/Calendar.jsx'
import Card from '../ui/Card.jsx'
import Button from '../ui/Button.jsx'
import ExerciseCard from './ExerciseCard.jsx'
import * as workoutService from '../../services/workoutService'

const STATUS_COLORS = {
  completed: 'bg-primary',
  skipped: 'bg-error',
  rest: 'bg-on-surface-variant/40',
  upcoming: 'bg-secondary/60',
  missed: 'bg-error/40',
}

const STATUS_LABELS = {
  completed: 'Completed',
  skipped: 'Skipped',
  rest: 'Rest day',
  upcoming: 'Upcoming',
  missed: 'Missed',
  no_plan: 'No plan for this period',
}

function monthRange(year, month) {
  const start = new Date(year, month, 1)
  const end = new Date(year, month + 1, 0)
  return { start: start.toISOString().slice(0, 10), end: end.toISOString().slice(0, 10) }
}

export default function WorkoutCalendarView({ registrationDate }) {
  const today = new Date()
  const [year, setYear] = useState(today.getFullYear())
  const [month, setMonth] = useState(today.getMonth())
  const [days, setDays] = useState([])
  const [streak, setStreak] = useState(0)
  const [loading, setLoading] = useState(true)
  const [selectedDate, setSelectedDate] = useState(today.toISOString().slice(0, 10))

  useEffect(() => {
    let cancelled = false
    async function load() {
      setLoading(true)
      try {
        const { start, end } = monthRange(year, month)
        const data = await workoutService.getWorkoutCalendar(start, end)
        if (!cancelled) {
          setDays(data.days)
          setStreak(data.streak)
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    load()
    return () => {
      cancelled = true
    }
  }, [year, month])

  const dayStatus = useMemo(() => {
    const map = {}
    for (const d of days) {
      map[d.date] = d
    }
    return map
  }, [days])

  const selectedEntry = dayStatus[selectedDate]

  const goToPrevMonth = () => {
    if (month === 0) {
      setYear((y) => y - 1)
      setMonth(11)
    } else {
      setMonth((m) => m - 1)
    }
  }

  const goToNextMonth = () => {
    if (month === 11) {
      setYear((y) => y + 1)
      setMonth(0)
    } else {
      setMonth((m) => m + 1)
    }
  }

  const monthLabel = new Date(year, month, 1).toLocaleDateString(undefined, { month: 'long', year: 'numeric' })

  return (
    <div className="space-y-lg">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-sm">
          <Button variant="ghost" className="h-9 w-9 px-0" onClick={goToPrevMonth} aria-label="Previous month">
            ‹
          </Button>
          <h3 className="text-headline-sm text-on-surface w-[180px] text-center">{monthLabel}</h3>
          <Button variant="ghost" className="h-9 w-9 px-0" onClick={goToNextMonth} aria-label="Next month">
            ›
          </Button>
        </div>
        <div className="flex items-center gap-xs text-body-sm text-on-surface-variant">
          <span aria-hidden="true">🔥</span> <span className="font-medium text-on-surface">{streak}</span> day streak
        </div>
      </div>

      <Card>
        {loading ? (
          <div className="flex justify-center py-lg">
            <span className="h-6 w-6 rounded-full border-2 border-primary border-t-transparent animate-spin" />
          </div>
        ) : (
          <Calendar
            year={year}
            month={month}
            selectedDate={selectedDate}
            dayStatus={dayStatus}
            statusColors={STATUS_COLORS}
            minDate={registrationDate}
            onSelectDay={setSelectedDate}
          />
        )}

        <div className="flex flex-wrap gap-md mt-md text-body-sm text-on-surface-variant">
          {Object.entries(STATUS_COLORS).map(([key, color]) => (
            <span key={key} className="flex items-center gap-xs">
              <span aria-hidden="true" className={`h-1.5 w-1.5 rounded-full ${color}`} /> {STATUS_LABELS[key]}
            </span>
          ))}
        </div>
      </Card>

      <Card>
        <h3 className="text-headline-sm text-on-surface mb-sm">{selectedDate}</h3>
        {!selectedEntry || selectedEntry.status === 'no_plan' ? (
          <p className="text-body-md text-on-surface-variant">No plan existed for this period yet.</p>
        ) : selectedEntry.status === 'rest' ? (
          <p className="text-body-md text-on-surface-variant">Rest day — no exercises scheduled.</p>
        ) : (
          <>
            <div className="flex items-center justify-between mb-md">
              <p className="text-body-sm text-on-surface-variant">
                {selectedEntry.workout.focus?.replace('_', ' ')} · ~{selectedEntry.workout.duration_minutes} min
              </p>
              <span className="text-label-sm px-md h-8 rounded-full flex items-center bg-surface-container-high text-on-surface-variant">
                {STATUS_LABELS[selectedEntry.status]}
              </span>
            </div>
            {selectedEntry.workout.exercises.map((ex, i) => (
              <ExerciseCard key={ex.name + i} exercise={ex} index={i} />
            ))}
          </>
        )}
      </Card>
    </div>
  )
}
