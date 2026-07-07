from app.services.ai.provider import get_coach_provider
from app.services.ai.prompts import build_coach_prompt
from app.services.ai.coach_engine import build_coach_insight


def generate_coach_insight(context: dict) -> dict:
    """
    Returns {tip}. Same RuleBasedProvider pattern as workout/nutrition/adaptive
    generation — see app/services/ai/provider.py for how this swaps to a real
    Claude/ChatGPT call later without touching any caller.
    """
    prompt = build_coach_prompt(context)
    provider = get_coach_provider(build_coach_insight)
    result = provider.generate(prompt, context)
    return {**result, "prompt": prompt}
