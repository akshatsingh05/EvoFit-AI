from app.services.ai.provider import get_nutrition_provider
from app.services.ai.prompts import build_nutrition_prompt
from app.services.ai.nutrition_generator import build_nutrition_plan


def generate_nutrition_targets(context: dict) -> dict:
    """
    Returns target_calories/protein/carbs/fat, water_goal_ml, and meals.
    Same pattern as workout_ai_service: the prompt is built and returned
    even though the current provider doesn't call an external API yet.
    """
    prompt = build_nutrition_prompt(context)
    provider = get_nutrition_provider(build_nutrition_plan)
    result = provider.generate(prompt, context)
    result["prompt"] = prompt
    return result
