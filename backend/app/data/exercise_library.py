"""
Exercise library. This is a pool the workout generator selects from based on
the user's actual equipment access, experience, injuries, medical conditions,
and BMI — it is not itself a plan. Equipment tiers are cumulative: "full_gym"
access can also use "home_basic" and "none" exercises.

Fields:
- focus: full_body | lower_body | push | pull | cardio | yoga
- equipment: none | home_basic | full_gym (cumulative tier)
- level: beginner | intermediate | advanced (soft preference, not a hard filter —
  a hard filter would leave "none equipment + advanced" users with an empty pool)
- impact_level: low | high (low-impact preferred for higher-BMI or joint-injury profiles)
- order_priority: 1 = compound/main movement, 2 = isolation/accessory (compound-first ordering)
- injury_tags: excluded when the user has logged that injury
- contraindications: excluded when the user has logged that medical condition
"""

EQUIPMENT_TIER = {"none": 0, "home_basic": 1, "full_gym": 2}
LEVEL_RANK = {"beginner": 0, "intermediate": 1, "advanced": 2}

EXERCISES = [
    # ---------- Bodyweight (equipment: none) ----------
    {"name": "Bodyweight Squat", "focus": "lower_body", "equipment": "none", "level": "beginner", "impact_level": "low", "order_priority": 1, "injury_tags": ["left_knee", "right_knee"], "contraindications": [], "instructions": "Feet shoulder-width apart, lower hips back and down, keep chest up."},
    {"name": "Walking Lunge", "focus": "lower_body", "equipment": "none", "level": "beginner", "impact_level": "low", "order_priority": 1, "injury_tags": ["left_knee", "right_knee"], "contraindications": [], "instructions": "Step forward, lower back knee toward floor, alternate legs."},
    {"name": "Glute Bridge", "focus": "lower_body", "equipment": "none", "level": "beginner", "impact_level": "low", "order_priority": 2, "injury_tags": [], "contraindications": [], "instructions": "Lie on back, drive hips up squeezing glutes at the top."},
    {"name": "Bulgarian Split Squat (bodyweight)", "focus": "lower_body", "equipment": "none", "level": "intermediate", "impact_level": "low", "order_priority": 1, "injury_tags": ["left_knee", "right_knee"], "contraindications": [], "instructions": "Rear foot elevated on a chair, lower into a lunge on the front leg."},
    {"name": "Jump Squat", "focus": "lower_body", "equipment": "none", "level": "advanced", "impact_level": "high", "order_priority": 1, "injury_tags": ["left_knee", "right_knee", "ankle"], "contraindications": ["heart_condition"], "instructions": "Squat down then explode upward into a jump, land softly."},
    {"name": "Wall Sit", "focus": "lower_body", "equipment": "none", "level": "beginner", "impact_level": "low", "order_priority": 2, "injury_tags": ["left_knee", "right_knee"], "contraindications": [], "instructions": "Back against a wall, slide down to a seated position, hold."},

    {"name": "Push-Up", "focus": "push", "equipment": "none", "level": "beginner", "impact_level": "low", "order_priority": 1, "injury_tags": ["shoulder"], "contraindications": [], "instructions": "Hands under shoulders, lower chest to floor, keep core tight."},
    {"name": "Incline Push-Up", "focus": "push", "equipment": "none", "level": "beginner", "impact_level": "low", "order_priority": 1, "injury_tags": ["shoulder"], "contraindications": [], "instructions": "Hands on a raised surface, lower chest toward it, easier variation."},
    {"name": "Pike Push-Up", "focus": "push", "equipment": "none", "level": "intermediate", "impact_level": "low", "order_priority": 1, "injury_tags": ["shoulder"], "contraindications": [], "instructions": "Hips high in a pike position, lower head toward floor, press back up."},
    {"name": "Diamond Push-Up", "focus": "push", "equipment": "none", "level": "advanced", "impact_level": "low", "order_priority": 2, "injury_tags": ["shoulder"], "contraindications": [], "instructions": "Hands close together under chest, lower and press up for triceps emphasis."},
    {"name": "Chair Dip", "focus": "push", "equipment": "none", "level": "beginner", "impact_level": "low", "order_priority": 2, "injury_tags": ["shoulder"], "contraindications": [], "instructions": "Hands on a chair edge, lower hips toward floor bending elbows, press up."},

    {"name": "Superman Hold", "focus": "pull", "equipment": "none", "level": "beginner", "impact_level": "low", "order_priority": 2, "injury_tags": ["lower_back"], "contraindications": [], "instructions": "Lie face down, lift arms and legs slightly, hold and squeeze."},
    {"name": "Reverse Snow Angel", "focus": "pull", "equipment": "none", "level": "beginner", "impact_level": "low", "order_priority": 2, "injury_tags": ["shoulder"], "contraindications": [], "instructions": "Lie face down, arms at sides, sweep arms overhead squeezing shoulder blades."},
    {"name": "Towel Row (door anchor)", "focus": "pull", "equipment": "none", "level": "intermediate", "impact_level": "low", "order_priority": 1, "injury_tags": ["lower_back"], "contraindications": [], "instructions": "Loop a towel around a sturdy anchor, lean back, pull chest toward hands."},
    {"name": "Prone Y-T-W Raise", "focus": "pull", "equipment": "none", "level": "beginner", "impact_level": "low", "order_priority": 2, "injury_tags": ["shoulder"], "contraindications": [], "instructions": "Lie face down, raise arms in Y, T, then W shapes to work upper back."},

    {"name": "Plank", "focus": "full_body", "equipment": "none", "level": "beginner", "impact_level": "low", "order_priority": 2, "injury_tags": ["lower_back"], "contraindications": [], "instructions": "Forearms and toes on floor, body in a straight line, brace core."},
    {"name": "Bicycle Crunch", "focus": "full_body", "equipment": "none", "level": "beginner", "impact_level": "low", "order_priority": 2, "injury_tags": ["lower_back"], "contraindications": [], "instructions": "Alternate elbow to opposite knee while extending the other leg."},
    {"name": "Bear Crawl", "focus": "full_body", "equipment": "none", "level": "intermediate", "impact_level": "low", "order_priority": 1, "injury_tags": ["shoulder", "left_knee", "right_knee"], "contraindications": [], "instructions": "Hands and feet on floor, knees hovering, crawl forward with control."},
    {"name": "Burpee", "focus": "full_body", "equipment": "none", "level": "advanced", "impact_level": "high", "order_priority": 1, "injury_tags": ["shoulder", "left_knee", "right_knee", "lower_back"], "contraindications": ["heart_condition", "hypertension"], "instructions": "Squat, kick back to a plank, push-up, jump feet in, jump up."},

    {"name": "Mountain Climbers", "focus": "cardio", "equipment": "none", "level": "intermediate", "impact_level": "high", "order_priority": 1, "injury_tags": ["lower_back"], "contraindications": ["heart_condition"], "instructions": "In plank position, drive knees toward chest alternately at pace."},
    {"name": "Jumping Jacks", "focus": "cardio", "equipment": "none", "level": "beginner", "impact_level": "high", "order_priority": 1, "injury_tags": ["ankle"], "contraindications": ["heart_condition"], "instructions": "Jump feet out while raising arms overhead, return to start."},
    {"name": "Brisk Walk in Place", "focus": "cardio", "equipment": "none", "level": "beginner", "impact_level": "low", "order_priority": 1, "injury_tags": [], "contraindications": [], "instructions": "March in place at a brisk pace, swinging arms naturally."},
    {"name": "Step-Ups (chair or stair)", "focus": "cardio", "equipment": "none", "level": "beginner", "impact_level": "low", "order_priority": 1, "injury_tags": ["left_knee", "right_knee"], "contraindications": [], "instructions": "Step up onto a stair or sturdy chair and back down, alternate leading leg."},
    {"name": "High Knees", "focus": "cardio", "equipment": "none", "level": "intermediate", "impact_level": "high", "order_priority": 1, "injury_tags": ["ankle", "left_knee", "right_knee"], "contraindications": ["heart_condition"], "instructions": "Jog in place bringing knees up toward hip height quickly."},

    {"name": "Downward Dog to Cobra Flow", "focus": "yoga", "equipment": "none", "level": "beginner", "impact_level": "low", "order_priority": 2, "injury_tags": [], "contraindications": [], "instructions": "Flow slowly between downward dog and cobra, breathing deeply."},
    {"name": "Cat-Cow Flow", "focus": "yoga", "equipment": "none", "level": "beginner", "impact_level": "low", "order_priority": 2, "injury_tags": [], "contraindications": [], "instructions": "On hands and knees, alternate arching and rounding the spine with breath."},
    {"name": "Seated Forward Fold Stretch", "focus": "yoga", "equipment": "none", "level": "beginner", "impact_level": "low", "order_priority": 2, "injury_tags": [], "contraindications": [], "instructions": "Sit with legs extended, hinge forward from the hips, hold and breathe."},
    {"name": "Child's Pose", "focus": "yoga", "equipment": "none", "level": "beginner", "impact_level": "low", "order_priority": 2, "injury_tags": [], "contraindications": [], "instructions": "Kneel and sit back onto heels, reach arms forward, relax and breathe."},

    # ---------- Home basics (dumbbells / bands / bench) ----------
    {"name": "Dumbbell Goblet Squat", "focus": "lower_body", "equipment": "home_basic", "level": "beginner", "impact_level": "low", "order_priority": 1, "injury_tags": ["left_knee", "right_knee"], "contraindications": [], "instructions": "Hold one dumbbell at chest, squat keeping torso upright."},
    {"name": "Dumbbell Romanian Deadlift", "focus": "lower_body", "equipment": "home_basic", "level": "intermediate", "impact_level": "low", "order_priority": 1, "injury_tags": ["lower_back"], "contraindications": [], "instructions": "Hinge at hips keeping back flat, lower dumbbells along shins."},
    {"name": "Dumbbell Lunge", "focus": "lower_body", "equipment": "home_basic", "level": "beginner", "impact_level": "low", "order_priority": 1, "injury_tags": ["left_knee", "right_knee"], "contraindications": [], "instructions": "Hold dumbbells at sides, step into a lunge, alternate legs."},
    {"name": "Dumbbell Step-Up", "focus": "lower_body", "equipment": "home_basic", "level": "intermediate", "impact_level": "low", "order_priority": 1, "injury_tags": ["left_knee", "right_knee"], "contraindications": [], "instructions": "Holding dumbbells, step up onto a sturdy bench or step, alternate legs."},
    {"name": "Dumbbell Calf Raise", "focus": "lower_body", "equipment": "home_basic", "level": "beginner", "impact_level": "low", "order_priority": 2, "injury_tags": ["ankle"], "contraindications": [], "instructions": "Holding dumbbells at sides, rise onto toes and lower with control."},

    {"name": "Dumbbell Shoulder Press", "focus": "push", "equipment": "home_basic", "level": "intermediate", "impact_level": "low", "order_priority": 1, "injury_tags": ["shoulder"], "contraindications": [], "instructions": "Press dumbbells overhead from shoulder height, avoid arching back."},
    {"name": "Dumbbell Bench Press", "focus": "push", "equipment": "home_basic", "level": "intermediate", "impact_level": "low", "order_priority": 1, "injury_tags": ["shoulder"], "contraindications": [], "instructions": "On a bench, press dumbbells up over chest, control the descent."},
    {"name": "Dumbbell Floor Press", "focus": "push", "equipment": "home_basic", "level": "beginner", "impact_level": "low", "order_priority": 1, "injury_tags": ["shoulder"], "contraindications": [], "instructions": "Lying on the floor, press dumbbells up from chest level, elbows brush floor."},
    {"name": "Overhead Triceps Extension", "focus": "push", "equipment": "home_basic", "level": "beginner", "impact_level": "low", "order_priority": 2, "injury_tags": ["shoulder"], "contraindications": [], "instructions": "Hold one dumbbell overhead with both hands, lower behind head, extend."},
    {"name": "Dumbbell Lateral Raise", "focus": "push", "equipment": "home_basic", "level": "beginner", "impact_level": "low", "order_priority": 2, "injury_tags": ["shoulder"], "contraindications": [], "instructions": "Raise dumbbells out to the sides to shoulder height, lower with control."},

    {"name": "Dumbbell Row", "focus": "pull", "equipment": "home_basic", "level": "beginner", "impact_level": "low", "order_priority": 1, "injury_tags": ["lower_back"], "contraindications": [], "instructions": "Hinge at hips, pull dumbbell to hip keeping elbow close."},
    {"name": "Resistance Band Pull-Apart", "focus": "pull", "equipment": "home_basic", "level": "beginner", "impact_level": "low", "order_priority": 2, "injury_tags": ["shoulder"], "contraindications": [], "instructions": "Hold band at chest height, pull apart squeezing shoulder blades."},
    {"name": "Resistance Band Row", "focus": "pull", "equipment": "home_basic", "level": "beginner", "impact_level": "low", "order_priority": 1, "injury_tags": ["lower_back"], "contraindications": [], "instructions": "Anchor band, pull handles to torso squeezing shoulder blades together."},
    {"name": "Dumbbell Bicep Curl", "focus": "pull", "equipment": "home_basic", "level": "beginner", "impact_level": "low", "order_priority": 2, "injury_tags": [], "contraindications": [], "instructions": "Curl dumbbells to shoulders keeping elbows fixed at sides."},
    {"name": "Renegade Row", "focus": "pull", "equipment": "home_basic", "level": "advanced", "impact_level": "low", "order_priority": 1, "injury_tags": ["shoulder", "lower_back"], "contraindications": [], "instructions": "In a plank holding dumbbells, row one at a time while stabilizing the core."},

    {"name": "Dumbbell Thruster", "focus": "full_body", "equipment": "home_basic", "level": "advanced", "impact_level": "high", "order_priority": 1, "injury_tags": ["shoulder", "left_knee", "right_knee"], "contraindications": ["heart_condition"], "instructions": "Squat with dumbbells at shoulders, stand and press overhead in one motion."},
    {"name": "Dumbbell Deadlift", "focus": "full_body", "equipment": "home_basic", "level": "intermediate", "impact_level": "low", "order_priority": 1, "injury_tags": ["lower_back"], "contraindications": [], "instructions": "Hinge at hips with dumbbells in front of thighs, stand tall, lower with control."},

    # ---------- Full gym (machines / barbell / rack) ----------
    {"name": "Barbell Back Squat", "focus": "lower_body", "equipment": "full_gym", "level": "intermediate", "impact_level": "low", "order_priority": 1, "injury_tags": ["left_knee", "right_knee", "lower_back"], "contraindications": [], "instructions": "Bar on upper back, squat to depth keeping knees tracking over toes."},
    {"name": "Leg Press", "focus": "lower_body", "equipment": "full_gym", "level": "beginner", "impact_level": "low", "order_priority": 1, "injury_tags": ["left_knee", "right_knee"], "contraindications": [], "instructions": "Feet shoulder-width on platform, lower under control, press through heels."},
    {"name": "Leg Curl Machine", "focus": "lower_body", "equipment": "full_gym", "level": "beginner", "impact_level": "low", "order_priority": 2, "injury_tags": ["left_knee", "right_knee"], "contraindications": [], "instructions": "Curl pad toward glutes with control, avoid hips lifting off pad."},
    {"name": "Leg Extension Machine", "focus": "lower_body", "equipment": "full_gym", "level": "beginner", "impact_level": "low", "order_priority": 2, "injury_tags": ["left_knee", "right_knee"], "contraindications": [], "instructions": "Extend legs against pad with control, lower without dropping the weight."},
    {"name": "Bulgarian Split Squat (barbell)", "focus": "lower_body", "equipment": "full_gym", "level": "advanced", "impact_level": "low", "order_priority": 1, "injury_tags": ["left_knee", "right_knee"], "contraindications": [], "instructions": "Rear foot elevated on a bench, barbell on back, lower into a lunge."},

    {"name": "Barbell Bench Press", "focus": "push", "equipment": "full_gym", "level": "intermediate", "impact_level": "low", "order_priority": 1, "injury_tags": ["shoulder"], "contraindications": [], "instructions": "Lower bar to mid-chest with control, press back up to lockout."},
    {"name": "Cable Triceps Pushdown", "focus": "push", "equipment": "full_gym", "level": "beginner", "impact_level": "low", "order_priority": 2, "injury_tags": ["shoulder"], "contraindications": [], "instructions": "Push bar down keeping elbows pinned at sides."},
    {"name": "Machine Chest Press", "focus": "push", "equipment": "full_gym", "level": "beginner", "impact_level": "low", "order_priority": 1, "injury_tags": ["shoulder"], "contraindications": [], "instructions": "Press handles forward from chest level, control the return."},
    {"name": "Overhead Barbell Press", "focus": "push", "equipment": "full_gym", "level": "advanced", "impact_level": "low", "order_priority": 1, "injury_tags": ["shoulder"], "contraindications": [], "instructions": "Press barbell from shoulders to overhead lockout, brace the core."},

    {"name": "Barbell Deadlift", "focus": "pull", "equipment": "full_gym", "level": "advanced", "impact_level": "low", "order_priority": 1, "injury_tags": ["lower_back"], "contraindications": [], "instructions": "Hinge and grip bar, drive through floor keeping back flat."},
    {"name": "Lat Pulldown", "focus": "pull", "equipment": "full_gym", "level": "beginner", "impact_level": "low", "order_priority": 1, "injury_tags": ["shoulder"], "contraindications": [], "instructions": "Pull bar to upper chest, control the return, avoid swinging."},
    {"name": "Seated Cable Row", "focus": "pull", "equipment": "full_gym", "level": "beginner", "impact_level": "low", "order_priority": 1, "injury_tags": ["lower_back"], "contraindications": [], "instructions": "Pull handle to torso keeping back straight, squeeze shoulder blades."},
    {"name": "Assisted Pull-Up Machine", "focus": "pull", "equipment": "full_gym", "level": "intermediate", "impact_level": "low", "order_priority": 1, "injury_tags": ["shoulder"], "contraindications": [], "instructions": "Grip the bar, pull chin over the bar with machine assistance, lower with control."},
    {"name": "Cable Face Pull", "focus": "pull", "equipment": "full_gym", "level": "beginner", "impact_level": "low", "order_priority": 2, "injury_tags": ["shoulder"], "contraindications": [], "instructions": "Pull rope toward face at eye level, elbows high, squeeze shoulder blades."},

    {"name": "Kettlebell Swing", "focus": "full_body", "equipment": "full_gym", "level": "intermediate", "impact_level": "high", "order_priority": 1, "injury_tags": ["lower_back"], "contraindications": ["heart_condition"], "instructions": "Hinge and swing the kettlebell to chest height using hip drive."},

    {"name": "Treadmill Intervals", "focus": "cardio", "equipment": "full_gym", "level": "intermediate", "impact_level": "high", "order_priority": 1, "injury_tags": ["ankle"], "contraindications": ["heart_condition"], "instructions": "Alternate 30s fast pace with 90s recovery pace."},
    {"name": "Rowing Machine", "focus": "cardio", "equipment": "full_gym", "level": "beginner", "impact_level": "low", "order_priority": 1, "injury_tags": ["lower_back"], "contraindications": [], "instructions": "Drive with legs first, then pull with arms, reverse the sequence to return."},
    {"name": "Stationary Bike", "focus": "cardio", "equipment": "full_gym", "level": "beginner", "impact_level": "low", "order_priority": 1, "injury_tags": [], "contraindications": [], "instructions": "Pedal at a steady, moderate resistance and cadence."},
    {"name": "Elliptical Machine", "focus": "cardio", "equipment": "full_gym", "level": "beginner", "impact_level": "low", "order_priority": 1, "injury_tags": [], "contraindications": [], "instructions": "Maintain a steady pace with a smooth, low-impact stride."},
]


def _infer_equipment_tags(ex: dict) -> set:
    """
    Sprint 4: derives the *specific* piece(s) of equipment an exercise needs
    (dumbbells / barbell / resistance_bands / machines / pull_up_bar / bench)
    from its name, since the library only tracked a coarse tier before. Every
    exercise with `equipment == "none"` needs nothing and is always tagged
    "bodyweight_only" so a "Bodyweight Only" user preference never empties a
    pool for a focus the library actually covers bodyweight-only.
    """
    if ex["equipment"] == "none":
        return {"bodyweight_only"}

    name = ex["name"].lower()
    tags = set()
    if "dumbbell" in name:
        tags.add("dumbbells")
    if "barbell" in name:
        tags.add("barbell")
    if "band" in name:
        tags.add("resistance_bands")
    if any(k in name for k in ("machine", "cable", "pulldown", "leg press", "leg curl", "leg extension")):
        tags.add("machines")
    if "pull-up" in name or "pull up" in name:
        tags.add("pull_up_bar")
    if "bench" in name and "step" not in name:
        tags.add("bench")
    if not tags:
        # Fallback so every exercise still resolves to at least one concrete
        # tag rather than silently matching nothing.
        tags.add("dumbbells" if ex["equipment"] == "home_basic" else "machines")
    return tags


for _ex in EXERCISES:
    _ex["equipment_tags"] = _infer_equipment_tags(_ex)


def exercises_for(
    focus: str,
    equipment_access: str,
    exclude_injury_tags: set,
    exclude_conditions: set = None,
    prefer_low_impact: bool = False,
    equipment_tags: set | None = None,
    exclude_names: set | None = None,
) -> list:
    """
    Hard filters: equipment tier, injuries, medical contraindications — these
    never leave an empty pool for a valid focus/equipment combination given
    the library's coverage. `prefer_low_impact` is a soft sort preference
    (higher BMI or joint concerns), not a filter, so it can't empty the pool.

    Sprint 4: `equipment_tags`, when provided (a non-empty set from the
    user's Workout Preferences "Equipment Available" multi-select), is an
    additional hard filter — an exercise is only included if it needs
    nothing ("bodyweight_only") or its inferred equipment tag intersects the
    user's selection. This is what makes "Home + Bodyweight Only" actually
    exclude Bench Press / Cable Fly / Lat Pulldown rather than just using the
    coarse tier. `exclude_names` drops specific exercises the user dislikes
    or that generation_service.py has flagged via injury/avoid-movement text.
    """
    max_tier = EQUIPMENT_TIER.get(equipment_access, 0)
    exclude_conditions = exclude_conditions or set()
    exclude_names = exclude_names or set()

    pool = [
        ex
        for ex in EXERCISES
        if ex["focus"] == focus
        and ex["name"] not in exclude_names
        and EQUIPMENT_TIER.get(ex["equipment"], 0) <= max_tier
        and not (set(ex["injury_tags"]) & exclude_injury_tags)
        and not (set(ex.get("contraindications", [])) & exclude_conditions)
        and (not equipment_tags or (ex["equipment_tags"] & (equipment_tags | {"bodyweight_only"})))
    ]

    if prefer_low_impact:
        pool = sorted(pool, key=lambda ex: 0 if ex.get("impact_level") == "low" else 1)

    return pool


def find_exercise_by_name(name: str) -> dict | None:
    return next((ex for ex in EXERCISES if ex["name"] == name), None)


def all_focuses() -> list[str]:
    return sorted({ex["focus"] for ex in EXERCISES})
