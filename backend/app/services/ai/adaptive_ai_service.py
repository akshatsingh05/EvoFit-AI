from app.services.ai.provider import get_adaptive_provider
from app.services.ai.prompts import build_adaptive_prompt
from app.services.ai.adaptive_engine import build_adaptive_analysis


def generate_adaptive_analysis(context: dict) -> dict:
    """
    Returns recovery_score, consistency_pct, fatigue_flag, intensity_modifier,
    and recommendations. Same RuleBasedProvider pattern as workout/nutrition
    generation — see provider.py for how this swaps to a real Claude call.
    """
    prompt = build_adaptive_prompt(context)
    provider = get_adaptive_provider(build_adaptive_analysis)
    result = provider.generate(prompt, context)
    return {**result, "prompt": prompt}
