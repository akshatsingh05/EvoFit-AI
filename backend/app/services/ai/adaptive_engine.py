"""
Deterministic adaptive-coaching analysis. This is the `builder` function
passed to RuleBasedProvider (same pattern as workout_generator.py and
nutrition_generator.py — see app/services/ai/provider.py). Every signal here
is computed from real rows the user generated: daily check-ins, workout
completions, and weight logs. Nothing is randomly generated or hardcoded.
"""

MOOD_SCORE = {"great": 100, "good": 80, "okay": 60, "low": 35, "bad": 15}


def _avg(values: list[float]) -> float | None:
    values = [v for v in values if v is not None]
    return sum(values) / len(values) if values else None


def build_adaptive_analysis(context: dict) -> dict:
    checkins = context.get("recent_checkins") or []
    workout_completions = context.get("recent_workout_statuses") or []  # list of "completed"|"skipped"
    scheduled_training_days = context.get("scheduled_training_days", 0)
    medical = context.get("medical") or {}
    weight_history = context.get("weight_history") or []  # list of {log_date, weight_kg}, chronological
    primary_goal = (context.get("goals") or {}).get("primary_goal")

    recommendations: list[str] = []

    # --- Recovery score: weighted blend of real check-in signals ---
    if checkins:
        avg_sleep = _avg([c["sleep_hours"] for c in checkins])
        avg_energy = _avg([c["energy_level"] for c in checkins])  # 1-5
        avg_soreness = _avg([c["muscle_soreness"] for c in checkins])  # 1-5, higher = more sore
        avg_pain = _avg([c["pain_level"] for c in checkins])  # 0-5, higher = more pain
        avg_mood = _avg([MOOD_SCORE.get(c["mood"], 60) for c in checkins])

        sleep_score = min(avg_sleep / 8.0, 1.0) * 100 if avg_sleep is not None else 60
        energy_score = (avg_energy / 5.0) * 100 if avg_energy is not None else 60
        soreness_score = max(0, 100 - (avg_soreness / 5.0) * 100) if avg_soreness is not None else 60
        pain_score = max(0, 100 - (avg_pain / 5.0) * 100) if avg_pain is not None else 100
        mood_score = avg_mood if avg_mood is not None else 60

        recovery_score = round(
            sleep_score * 0.30 + energy_score * 0.25 + soreness_score * 0.20 + pain_score * 0.15 + mood_score * 0.10
        )

        if avg_sleep is not None and avg_sleep < 6:
            recommendations.append(
                f"Your sleep has averaged {avg_sleep:.1f}h over your recent check-ins — aim for 7+ hours to support recovery."
            )
        if avg_pain is not None and avg_pain >= 3:
            recommendations.append(
                "You've reported meaningful pain in recent check-ins. Consider deloading affected areas and consulting a professional if it persists."
            )
        if avg_soreness is not None and avg_soreness >= 4:
            recommendations.append("Muscle soreness has been high — today's plan has been scaled back slightly to let you recover.")
    else:
        recovery_score = 60  # neutral default until check-ins exist
        recommendations.append("Complete a daily check-in to get a personalized recovery score.")

    # --- Consistency: real completion rate against the actual schedule ---
    completed_count = sum(1 for s in workout_completions if s == "completed")
    total_logged = len(workout_completions)
    if scheduled_training_days > 0:
        consistency_pct = round(min(completed_count / scheduled_training_days, 1.0) * 100)
    elif total_logged > 0:
        consistency_pct = round((completed_count / total_logged) * 100)
    else:
        consistency_pct = 0

    if total_logged > 0 and consistency_pct < 50:
        recommendations.append(
            f"You've completed {completed_count} of your last {total_logged} logged workouts. Try scheduling sessions at a fixed time to build consistency."
        )
    elif consistency_pct >= 80 and total_logged >= 3:
        recommendations.append("Strong consistency this week — this is exactly what drives long-term progress.")

    # --- Fatigue flag ---
    fatigue_flag = recovery_score < 40 or (checkins and _avg([c["pain_level"] for c in checkins]) or 0) >= 3

    # --- Weight trend vs goal (real signal, not fabricated) ---
    nutrition_calorie_adjustment = 0.0
    if len(weight_history) >= 2:
        first_weight = weight_history[0]["weight_kg"]
        last_weight = weight_history[-1]["weight_kg"]
        change = last_weight - first_weight
        if primary_goal == "lose_weight" and change >= 0:
            nutrition_calorie_adjustment = -0.05
            recommendations.append(
                "Your weight hasn't trended down over your logged entries — nutrition targets have been adjusted slightly."
            )
        elif primary_goal == "build_muscle" and change <= 0:
            nutrition_calorie_adjustment = 0.05
            recommendations.append(
                "Your weight hasn't trended up despite a muscle-gain goal — nutrition targets have been adjusted slightly."
            )

    # --- Intensity modifier for the next generated workout ---
    if fatigue_flag:
        intensity_modifier = -1
        recommendations.append("Training intensity has been reduced slightly this week to prioritize recovery.")
    elif recovery_score >= 75 and consistency_pct >= 80:
        intensity_modifier = 1
        recommendations.append("Recovery and consistency are strong — training volume has been nudged up.")
    else:
        intensity_modifier = 0

    if medical.get("injuries"):
        recommendations.append(
            f"Exercises continue to avoid loading: {', '.join(medical['injuries'])}."
        )

    if not recommendations:
        recommendations.append("Everything looks on track — keep following your current plan.")

    return {
        "recovery_score": max(0, min(100, recovery_score)),
        "consistency_pct": consistency_pct,
        "fatigue_flag": bool(fatigue_flag),
        "intensity_modifier": intensity_modifier,
        "nutrition_calorie_adjustment": nutrition_calorie_adjustment,
        "recommendations": recommendations,
    }
