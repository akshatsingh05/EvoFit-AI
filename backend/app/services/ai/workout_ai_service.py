from app.services.ai.provider import get_workout_provider
from app.services.ai.prompts import build_workout_prompt
from app.services.ai.workout_generator import build_workout_plan


def generate_workout_schedule(context: dict) -> dict:
    """
    Returns {"schedule": [...]}. `context` should include goals,
    fitness_experience, and medical (conditions/injuries) from the user's
    real profile. The prompt is built and stored even though the current
    provider doesn't send it anywhere — it's what a Claude-backed provider
    will receive once wired in (see provider.py).
    """
    prompt = build_workout_prompt(context)
    provider = get_workout_provider(build_workout_plan)
    result = provider.generate(prompt, context)
    return {"schedule": result["schedule"], "prompt": prompt}
