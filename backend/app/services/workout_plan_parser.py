"""
Feature 1 - parses raw workout-plan text (typed manually, or extracted from
a TXT/PDF/DOCX/image upload by file_parsing_service) into the same shape the
rest of EvoFit AI already understands: a list of day objects with
exercises/sets/reps, comparable to WorkoutPlan.schedule.

Unknown exercises are always preserved verbatim (never dropped) even when
they can't be matched against the exercise library or tagged with a muscle
group -- the sprint spec calls this out explicitly.
"""
import re
import difflib
from collections import Counter

from app.data.exercise_library import EXERCISES

DAY_NAMES = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

# Ordered so the first matching keyword wins (e.g. "bench press" hits chest
# before it could ever hit the generic "press" -> shoulders rule).
MUSCLE_GROUP_KEYWORDS = [
    ("chest", ["bench", "chest", "fly", "flye", "pec", "dip"]),
    ("back", ["row", "pulldown", "pull-up", "pullup", "lat ", "deadlift", "shrug", "back"]),
    ("legs", ["squat", "leg", "lunge", "calf", "quad", "hamstring", "glute", "hip thrust"]),
    ("shoulders", ["shoulder", "overhead press", "military press", "delt", "lateral raise", "front raise",
                   "upright row", "arnold", "press"]),
    ("arms", ["curl", "bicep", "tricep", "skull crusher", "kickback", "forearm"]),
    ("core", ["plank", "crunch", "sit-up", "situp", "ab ", "abs", "core", "russian twist"]),
    ("cardio", ["run", "jog", "bike", "cycling", "cardio", "jump rope", "burpee", "rowing machine", "elliptical",
                "sprint", "treadmill", "stairmaster", "hiit"]),
]

EQUIPMENT_KEYWORDS = {
    "full_gym": ["barbell", "machine", "cable", "smith machine", "leg press", "lat pulldown", "chest press machine"],
    "home_basic": ["dumbbell", "band", "kettlebell", "bench"],
    "none": ["bodyweight", "push-up", "pushup", "pull-up", "pullup", "no equipment", "air squat"],
}

REP_LINE_RE = re.compile(
    r"^(?P<name>.+?)[\s:\-–—]*"
    r"(?:(?P<sets>\d+)\s*(?:x|sets?\s*(?:of|x)?)\s*(?P<reps>\d+(?:\s*-\s*\d+)?))?"
    r"\s*(?:reps?)?\s*$",
    re.IGNORECASE,
)
SETS_X_REPS_RE = re.compile(r"(\d+)\s*x\s*(\d+(?:\s*-\s*\d+)?)", re.IGNORECASE)
SETS_OF_REPS_RE = re.compile(r"(\d+)\s*sets?\s*(?:of|x)?\s*(\d+(?:\s*-\s*\d+)?)\s*reps?", re.IGNORECASE)
REST_WORDS = ("rest day", "rest", "off day", "recovery day")

_LIBRARY_NAMES = [ex["name"] for ex in EXERCISES]
_LIBRARY_BY_NAME = {ex["name"].lower(): ex for ex in EXERCISES}


def _clean_line(line: str) -> str:
    line = line.strip()
    line = re.sub(r"^[\-\*\u2022•]+\s*", "", line)  # bullet markers
    line = re.sub(r"^\d+[\.\)]\s*", "", line)  # "1. " / "1) " numbered lists
    line = line.replace("|", " ").strip()
    return line


def _is_day_header(line: str) -> tuple[bool, str | None]:
    lowered = line.lower().strip().rstrip(":")
    for day in DAY_NAMES:
        if lowered == day or lowered.startswith(day + " ") or lowered.startswith(day + ","):
            return True, line.strip().rstrip(":")
    day_n_match = re.match(r"^day\s*\d+\b", lowered)
    if day_n_match:
        return True, line.strip().rstrip(":")
    # Short standalone label lines like "Push Day", "Leg Day", "Upper Body"
    if len(lowered.split()) <= 4 and re.search(r"\b(day|push|pull|legs?|upper|lower|full body)\b", lowered) and not re.search(r"\d+\s*x\s*\d+", lowered):
        if not any(kw in lowered for kw in ("set", "rep", "min", "sec")):
            return True, line.strip().rstrip(":")
    return False, None


def _is_rest_line(line: str) -> bool:
    lowered = line.lower().strip()
    return any(lowered == w or lowered.startswith(w) for w in REST_WORDS)


def _extract_sets_reps(line: str) -> tuple[str, int | None, str | None]:
    """Returns (exercise_name_without_numbers, sets, reps_str)."""
    m = SETS_X_REPS_RE.search(line)
    if not m:
        m = SETS_OF_REPS_RE.search(line)
    if m:
        sets = int(m.group(1))
        reps = m.group(2).replace(" ", "")
        name = (line[: m.start()] + line[m.end():]).strip(" -:–—x")
        return name.strip(), sets, reps
    return line.strip(), None, None


def _match_library_exercise(name: str) -> dict | None:
    lowered = name.lower().strip()
    if lowered in _LIBRARY_BY_NAME:
        return _LIBRARY_BY_NAME[lowered]
    matches = difflib.get_close_matches(lowered, list(_LIBRARY_BY_NAME.keys()), n=1, cutoff=0.72)
    if matches:
        return _LIBRARY_BY_NAME[matches[0]]
    # Substring match (handles "Barbell Bench Press" vs "Bench Press")
    for lib_name_lower, ex in _LIBRARY_BY_NAME.items():
        if lib_name_lower in lowered or lowered in lib_name_lower:
            return ex
    return None


def _infer_muscle_group(name: str, library_focus: str | None) -> str:
    lowered = name.lower()
    for group, keywords in MUSCLE_GROUP_KEYWORDS:
        if any(kw in lowered for kw in keywords):
            return group
    if library_focus == "push":
        return "chest"
    if library_focus == "pull":
        return "back"
    if library_focus == "lower_body":
        return "legs"
    if library_focus == "cardio":
        return "cardio"
    if library_focus == "yoga":
        return "core"
    return "unknown"


def _infer_equipment(all_lines: list[str]) -> str:
    text = " ".join(all_lines).lower()
    scores = {tier: sum(text.count(kw) for kw in kws) for tier, kws in EQUIPMENT_KEYWORDS.items()}
    if scores["full_gym"] > 0:
        return "full_gym"
    if scores["home_basic"] > 0:
        return "home_basic"
    if scores["none"] > 0:
        return "none"
    return "unspecified"


def _infer_training_style(rep_values: list[int]) -> str:
    if not rep_values:
        return "unspecified"
    avg = sum(rep_values) / len(rep_values)
    if avg <= 6:
        return "strength"
    if avg <= 12:
        return "hypertrophy"
    return "endurance"


def _infer_split(days: list[dict]) -> str:
    training_days = [d for d in days if not d["is_rest_day"] and d["exercises"]]
    if not training_days:
        return "unspecified"

    day_dominant_groups = []
    for day in training_days:
        groups = [ex["muscle_group"] for ex in day["exercises"] if ex["muscle_group"] != "unknown"]
        if not groups:
            day_dominant_groups.append("unknown")
            continue
        day_dominant_groups.append(Counter(groups).most_common(1)[0][0])

    unique_groups = set(day_dominant_groups) - {"unknown"}
    if len(training_days) <= 1:
        return "single day"
    if all(g == "unknown" for g in day_dominant_groups):
        return "custom split"
    if len(unique_groups) >= min(4, len(training_days)):
        return "body part split"
    if unique_groups <= {"chest", "back", "shoulders", "arms"} and len(unique_groups) >= 2:
        return "push pull legs" if "legs" in unique_groups else "upper/lower split"
    if len(unique_groups) == 1 and list(unique_groups)[0] not in ("unknown",):
        # every day trains the same broad category -> likely full body
        return "full body"
    return "custom split"


def parse_workout_text(raw_text: str) -> dict:
    lines = [_clean_line(l) for l in raw_text.splitlines()]
    lines = [l for l in lines if l != ""]

    days: list[dict] = []
    current_day = None
    unassigned_exercises: list[str] = []  # exercise lines before any day header

    for line in lines:
        is_header, header_label = _is_day_header(line)
        if is_header:
            current_day = {"day_name": header_label, "is_rest_day": False, "exercises": []}
            days.append(current_day)
            continue

        if _is_rest_line(line):
            if current_day is not None and not current_day["exercises"]:
                current_day["is_rest_day"] = True
                current_day["day_name"] = current_day["day_name"] or line
            else:
                days.append({"day_name": line, "is_rest_day": True, "exercises": []})
                current_day = None
            continue

        # It's an exercise line
        name, sets, reps = _extract_sets_reps(line)
        if not name:
            continue
        library_match = _match_library_exercise(name)
        muscle_group = _infer_muscle_group(name, library_match["focus"] if library_match else None)
        exercise_entry = {
            "name": name,
            "matched_library_name": library_match["name"] if library_match else None,
            "focus": library_match["focus"] if library_match else "unknown",
            "muscle_group": muscle_group,
            "sets": sets,
            "reps": reps,
            "raw_line": line,
        }
        if current_day is None:
            unassigned_exercises.append(exercise_entry)
        else:
            current_day["exercises"].append(exercise_entry)

    # If the whole plan had no day headers at all (e.g. a flat exercise
    # list), treat it as a single unnamed training day rather than
    # discarding the exercises.
    if unassigned_exercises and not days:
        days.append({"day_name": "Day 1", "is_rest_day": False, "exercises": unassigned_exercises})
    elif unassigned_exercises:
        days.insert(0, {"day_name": "Day 1", "is_rest_day": False, "exercises": unassigned_exercises})

    all_exercises = [ex for d in days for ex in d["exercises"]]
    rep_values = []
    for ex in all_exercises:
        if ex["reps"]:
            low = re.match(r"\d+", ex["reps"])
            if low:
                rep_values.append(int(low.group()))

    muscle_volume: dict[str, int] = {}
    for ex in all_exercises:
        weight = ex["sets"] if ex["sets"] else 1
        muscle_volume[ex["muscle_group"]] = muscle_volume.get(ex["muscle_group"], 0) + weight

    workout_days_count = sum(1 for d in days if not d["is_rest_day"] and d["exercises"])
    rest_days_count = sum(1 for d in days if d["is_rest_day"])

    return {
        "days": days,
        "workout_days_count": workout_days_count,
        "rest_days_count": rest_days_count,
        "total_exercises": len(all_exercises),
        "unmatched_exercise_count": sum(1 for ex in all_exercises if ex["matched_library_name"] is None),
        "equipment_guess": _infer_equipment(lines),
        "training_style_guess": _infer_training_style(rep_values),
        "detected_split": _infer_split(days),
        "muscle_volume": muscle_volume,
    }
