"""
Prompt builders for future LLM integration. These produce the exact prompt
text a real Claude API call would send; today that text is constructed and
stored on the plan (`generation_basis.prompt`) but not sent anywhere, since
RuleBasedProvider generates the plan algorithmically instead. Once an LLM
provider is wired in, these prompts are what it will receive.
"""


def build_workout_prompt(context: dict) -> str:
    goals = context.get("goals") or {}
    fitness = context.get("fitness_experience") or {}
    medical = context.get("medical") or {}

    return (
        "You are a certified strength & conditioning coach. Build a 7-day workout schedule "
        f"for a client with primary goal '{goals.get('primary_goal')}', "
        f"experience level '{fitness.get('experience_level')}', "
        f"currently training {fitness.get('workouts_per_week_current')} days/week, "
        f"with access to: {fitness.get('equipment_access')}. "
        f"Preferred workout types: {fitness.get('preferred_workout_types')}. "
        f"Known injuries to avoid loading: {medical.get('injuries') or 'none reported'}. "
        f"Medical conditions to account for: {medical.get('conditions') or 'none reported'}. "
        "For each day, decide whether it is a training day or rest day, and for training days "
        "list exercises with sets, reps, rest time in seconds, brief form instructions, and an "
        "estimated total session duration in minutes. Return structured JSON only."
    )


def build_nutrition_prompt(context: dict) -> str:
    goals = context.get("goals") or {}
    body = context.get("body_metrics") or {}
    lifestyle = context.get("lifestyle_diet") or {}
    medical = context.get("medical") or {}

    return (
        "You are a registered dietitian. Build a one-day meal plan (breakfast, lunch, snack, "
        f"dinner) for a client whose goal is '{goals.get('primary_goal')}', "
        f"height {body.get('height_cm')}cm, weight {body.get('weight_kg')}kg, age {body.get('age')}, "
        f"sex {body.get('sex')}, activity level '{lifestyle.get('occupation_activity')}', "
        f"training {context.get('workouts_per_week', 0)} days/week, "
        f"diet preference '{lifestyle.get('diet_type')}', eating {lifestyle.get('meals_per_day')} meals/day. "
        f"Allergies to avoid: {medical.get('allergies') or 'none reported'}. "
        "Calculate appropriate daily calorie and macro (protein/carbs/fat) targets and a water "
        "intake goal in milliliters, then assign each meal a name, calories, protein, carbs and "
        "fat. Return structured JSON only."
    )


def build_adaptive_prompt(context: dict) -> str:
    checkins = context.get("recent_checkins") or []
    workout_completions = context.get("recent_workout_statuses") or []
    weight_history = context.get("weight_history") or []
    goals = context.get("goals") or {}
    medical = context.get("medical") or {}

    return (
        "You are an adaptive fitness coach reviewing a client's recent data. "
        f"Over the last {len(checkins)} daily check-ins, review sleep hours, energy level, "
        "muscle soreness, pain level, and mood. "
        f"Workout completion record: {workout_completions}. "
        f"Weight log entries: {weight_history}. "
        f"Primary goal: {goals.get('primary_goal')}. "
        f"Known injuries/conditions to respect: {medical.get('injuries')} / {medical.get('conditions')}. "
        "Compute a recovery score (0-100), a training consistency percentage, whether the client "
        "shows signs of fatigue, whether next week's training intensity should decrease, stay the "
        "same, or increase, and give 2-4 short, specific coaching recommendations grounded in the "
        "data above. Return structured JSON only."
    )


def build_coach_prompt(context: dict) -> str:
    goals = context.get("goals") or {}

    return (
        "You are a personal AI fitness coach writing a single short, encouraging, non-repetitive "
        f"message for today's dashboard. The client's primary goal is '{goals.get('primary_goal')}'. "
        f"Latest recovery score: {context.get('recovery_score')}/100. "
        f"Training consistency: {context.get('consistency_pct')}%. "
        f"Fatigue flag: {context.get('fatigue_flag')}. "
        f"Nutrition adherence (last 14 days): {context.get('nutrition_adherence_pct')}%. "
        f"Current workout streak: {context.get('workout_streak_days')} days. "
        f"Weight trend relative to goal: {context.get('weight_trend')}. "
        "Prioritize acute recovery concerns first, then streak momentum, then adherence, then weight "
        "trend, then a goal-appropriate general tip. Return one sentence, plain text only."
    )
