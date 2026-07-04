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
