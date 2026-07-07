"""
Deterministic AI Coach tip synthesis — same RuleBasedProvider pattern as
adaptive_engine.py (see app/services/ai/provider.py for how this swaps to a
real Claude/ChatGPT call later). Combines the latest adaptive insight, weight
trend vs goal, nutrition adherence, and workout streak into one short,
personalized coaching message. Several phrasings exist per situation so the
tip varies day to day rather than repeating the exact same sentence forever.
"""


def _pick(variants: list[str], variety_seed: int) -> str:
    return variants[variety_seed % len(variants)]


GOAL_DEFAULT_TIPS = {
    "build_muscle": [
        "Consistency beats intensity for muscle growth — focus on hitting every planned session this week.",
        "Progressive overload matters more than perfect days. Small, consistent gains add up.",
    ],
    "lose_weight": [
        "Small, sustainable calorie deficits work best — pair your workouts with consistent meal timing.",
        "Fat loss responds to consistency over weeks, not perfection on any single day.",
    ],
    "improve_endurance": [
        "Keep most of your cardio easy and reserve hard efforts for 1-2 sessions a week.",
        "Endurance builds from accumulated easy volume — resist the urge to go hard every session.",
    ],
}

FALLBACK_TIPS = [
    "Check today's workout and nutrition plan to keep your streak going.",
    "Stay on top of today's plan — small, consistent actions compound into real progress.",
]


def build_coach_insight(context: dict) -> dict:
    if not context.get("has_onboarding"):
        return {"tip": "Finish onboarding so your AI coach can start building your first plan."}

    goals = context.get("goals") or {}
    primary_goal = goals.get("primary_goal")
    recovery_score = context.get("recovery_score")
    consistency_pct = context.get("consistency_pct")
    fatigue_flag = context.get("fatigue_flag", False)
    nutrition_adherence_pct = context.get("nutrition_adherence_pct")
    workout_streak_days = context.get("workout_streak_days", 0)
    weight_trend = context.get("weight_trend")  # "stalled_loss" | "stalled_gain" | None
    variety_seed = context.get("variety_seed", 0)

    # Priority: acute recovery concerns > streak momentum > adherence > weight trend > goal default.
    if recovery_score is None:
        tip = "Complete a daily check-in so your AI coach can start tailoring today's advice to how you feel."
    elif fatigue_flag:
        tip = _pick(
            [
                "Your recovery signals are low today — consider a lighter session or an extra rest day.",
                "Sleep, soreness, and pain trends suggest you're due for recovery, not another hard push.",
                "Recovery looks strained right now; scaling back intensity today will pay off later this week.",
            ],
            variety_seed,
        )
    elif workout_streak_days >= 5:
        tip = _pick(
            [
                f"{workout_streak_days}-day streak — this is exactly the consistency that drives real results.",
                f"You're {workout_streak_days} days deep in your streak. Keep the momentum going.",
                f"A {workout_streak_days}-day streak like this compounds fast — don't stop now.",
            ],
            variety_seed,
        )
    elif nutrition_adherence_pct is not None and nutrition_adherence_pct < 50:
        tip = _pick(
            [
                "Your logged meals have been inconsistent lately — try logging right after eating so nothing slips.",
                "Nutrition adherence has dipped recently. Prepping a meal or two ahead of time can help a lot.",
            ],
            variety_seed,
        )
    elif weight_trend == "stalled_loss" and primary_goal == "lose_weight":
        tip = _pick(
            [
                "Your weight hasn't trended down recently — nutrition targets have been nudged to help restart progress.",
                "Progress on the scale has stalled. Small, sustainable calorie deficits work better than big cuts.",
            ],
            variety_seed,
        )
    elif weight_trend == "stalled_gain" and primary_goal == "build_muscle":
        tip = _pick(
            [
                "Weight hasn't trended up despite your muscle-gain goal — targets have been adjusted upward a bit.",
                "Building muscle needs a slight surplus; your nutrition targets now reflect that a bit more.",
            ],
            variety_seed,
        )
    elif consistency_pct is not None and consistency_pct >= 80:
        tip = _pick(
            [
                "Strong training consistency lately — this is what turns a plan into real progress.",
                "You're hitting your planned sessions consistently. Keep stacking weeks like this.",
            ],
            variety_seed,
        )
    else:
        tip = _pick(GOAL_DEFAULT_TIPS.get(primary_goal, FALLBACK_TIPS), variety_seed)

    return {"tip": tip}
