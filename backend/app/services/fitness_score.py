"""
Shared by dashboard_service and progress_service. Extracted to its own
module so neither has to import the other (dashboard_service now depends on
adaptive_service, which depends on progress_service — importing this
function from dashboard_service directly would create a cycle).
"""

EXPERIENCE_POINTS = {"beginner": 20, "intermediate": 45, "advanced": 70}
EQUIPMENT_POINTS = {"none": 5, "home_basic": 10, "full_gym": 15}


def compute_fitness_score(onboarding) -> tuple[int, str]:
    """
    Baseline fitness score (0-100) derived purely from onboarding answers:
    experience level, current weekly training frequency, and equipment access.
    This is a starting point only — the adaptive engine's recovery_score is
    the metric that responds to real day-to-day data.
    """
    fitness_experience = onboarding.fitness_experience
    if not fitness_experience:
        return 0, "Complete onboarding to calculate your baseline score"

    experience_score = EXPERIENCE_POINTS.get(fitness_experience.get("experience_level"), 0)
    frequency_score = min(int(fitness_experience.get("workouts_per_week_current", 0)) * 3, 15)
    equipment_score = EQUIPMENT_POINTS.get(fitness_experience.get("equipment_access"), 0)

    score = min(experience_score + frequency_score + equipment_score, 100)
    return score, "Baseline score from your experience level, current training frequency, and equipment access"
