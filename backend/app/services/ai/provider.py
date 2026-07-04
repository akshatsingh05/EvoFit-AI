"""
AI provider abstraction.

Every plan-generation service in this app calls a provider through this
interface rather than talking to rule-based logic directly. Today,
`RuleBasedProvider` is the only implementation — it deterministically builds
a plan from the user's real profile data (no network calls, no API key
required). To integrate Claude or another LLM later:

    1. Implement a new class below (e.g. `ClaudeProvider`) that satisfies
       `AIProvider` and calls the real API with the prompt string.
    2. Change `get_workout_provider()` / `get_nutrition_provider()` to return
       that class instead.

No changes are needed in workout_ai_service.py, nutrition_ai_service.py, or
any router/service that consumes them — they only depend on this interface.
"""
from abc import ABC, abstractmethod


class AIProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, context: dict) -> dict:
        """
        Takes a natural-language prompt (what would be sent to an LLM) plus
        the structured context it was built from, and returns a structured
        plan as a dict. A real LLM-backed provider would send `prompt` to the
        model and parse its response into the same dict shape.
        """
        raise NotImplementedError


class RuleBasedProvider(AIProvider):
    """
    Deterministic placeholder. `generate` ignores the prompt text (there's no
    model to send it to yet) and instead calls the `builder` function passed
    in with the same context, so behavior is 100% derived from real user data
    — never hardcoded to a single output — while keeping today's interface
    identical to what an LLM-backed provider will expose.
    """

    def __init__(self, builder):
        self._builder = builder

    def generate(self, prompt: str, context: dict) -> dict:
        return self._builder(context)


def get_workout_provider(builder) -> AIProvider:
    return RuleBasedProvider(builder)


def get_nutrition_provider(builder) -> AIProvider:
    return RuleBasedProvider(builder)
