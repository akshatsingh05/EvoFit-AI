"""
Exercise library. This is a pool the workout generator selects from based on
the user's actual equipment access, experience, and injuries — it is not
itself a plan. Equipment tiers are cumulative: "full_gym" access can also use
"home_basic" and "none" exercises.
"""

EQUIPMENT_TIER = {"none": 0, "home_basic": 1, "full_gym": 2}

EXERCISES = [
    # Full body / bodyweight (equipment: none)
    {"name": "Bodyweight Squat", "focus": "full_body", "equipment": "none", "injury_tags": ["left_knee", "right_knee"], "instructions": "Feet shoulder-width apart, lower hips back and down, keep chest up."},
    {"name": "Push-Up", "focus": "full_body", "equipment": "none", "injury_tags": ["shoulder"], "instructions": "Hands under shoulders, lower chest to floor, keep core tight."},
    {"name": "Walking Lunge", "focus": "lower_body", "equipment": "none", "injury_tags": ["left_knee", "right_knee"], "instructions": "Step forward, lower back knee toward floor, alternate legs."},
    {"name": "Plank", "focus": "full_body", "equipment": "none", "injury_tags": ["lower_back"], "instructions": "Forearms and toes on floor, body in a straight line, brace core."},
    {"name": "Glute Bridge", "focus": "lower_body", "equipment": "none", "injury_tags": [], "instructions": "Lie on back, drive hips up squeezing glutes at the top."},
    {"name": "Mountain Climbers", "focus": "cardio", "equipment": "none", "injury_tags": ["lower_back"], "instructions": "In plank position, drive knees toward chest alternately at pace."},
    {"name": "Jumping Jacks", "focus": "cardio", "equipment": "none", "injury_tags": ["ankle"], "instructions": "Jump feet out while raising arms overhead, return to start."},
    {"name": "Superman Hold", "focus": "pull", "equipment": "none", "injury_tags": ["lower_back"], "instructions": "Lie face down, lift arms and legs slightly, hold and squeeze."},
    {"name": "Bicycle Crunch", "focus": "full_body", "equipment": "none", "injury_tags": ["lower_back"], "instructions": "Alternate elbow to opposite knee while extending the other leg."},
    {"name": "Downward Dog to Cobra Flow", "focus": "yoga", "equipment": "none", "injury_tags": [], "instructions": "Flow slowly between downward dog and cobra, breathing deeply."},
    {"name": "Cat-Cow Flow", "focus": "yoga", "equipment": "none", "injury_tags": [], "instructions": "On hands and knees, alternate arching and rounding the spine with breath."},
    {"name": "Seated Forward Fold Stretch", "focus": "yoga", "equipment": "none", "injury_tags": [], "instructions": "Sit with legs extended, hinge forward from the hips, hold and breathe."},

    # Home basics (dumbbells / bands / bench)
    {"name": "Dumbbell Goblet Squat", "focus": "lower_body", "equipment": "home_basic", "injury_tags": ["left_knee", "right_knee"], "instructions": "Hold one dumbbell at chest, squat keeping torso upright."},
    {"name": "Dumbbell Row", "focus": "pull", "equipment": "home_basic", "injury_tags": ["lower_back"], "instructions": "Hinge at hips, pull dumbbell to hip keeping elbow close."},
    {"name": "Dumbbell Shoulder Press", "focus": "push", "equipment": "home_basic", "injury_tags": ["shoulder"], "instructions": "Press dumbbells overhead from shoulder height, avoid arching back."},
    {"name": "Dumbbell Romanian Deadlift", "focus": "lower_body", "equipment": "home_basic", "injury_tags": ["lower_back"], "instructions": "Hinge at hips keeping back flat, lower dumbbells along shins."},
    {"name": "Resistance Band Pull-Apart", "focus": "pull", "equipment": "home_basic", "injury_tags": ["shoulder"], "instructions": "Hold band at chest height, pull apart squeezing shoulder blades."},
    {"name": "Dumbbell Bench Press", "focus": "push", "equipment": "home_basic", "injury_tags": ["shoulder"], "instructions": "On a bench, press dumbbells up over chest, control the descent."},
    {"name": "Dumbbell Lunge", "focus": "lower_body", "equipment": "home_basic", "injury_tags": ["left_knee", "right_knee"], "instructions": "Hold dumbbells at sides, step into a lunge, alternate legs."},
    {"name": "Dumbbell Bicep Curl", "focus": "pull", "equipment": "home_basic", "injury_tags": [], "instructions": "Curl dumbbells to shoulders keeping elbows fixed at sides."},
    {"name": "Overhead Triceps Extension", "focus": "push", "equipment": "home_basic", "injury_tags": ["shoulder"], "instructions": "Hold one dumbbell overhead with both hands, lower behind head, extend."},

    # Full gym (machines / barbell / rack)
    {"name": "Barbell Back Squat", "focus": "lower_body", "equipment": "full_gym", "injury_tags": ["left_knee", "right_knee", "lower_back"], "instructions": "Bar on upper back, squat to depth keeping knees tracking over toes."},
    {"name": "Barbell Bench Press", "focus": "push", "equipment": "full_gym", "injury_tags": ["shoulder"], "instructions": "Lower bar to mid-chest with control, press back up to lockout."},
    {"name": "Barbell Deadlift", "focus": "pull", "equipment": "full_gym", "injury_tags": ["lower_back"], "instructions": "Hinge and grip bar, drive through floor keeping back flat."},
    {"name": "Lat Pulldown", "focus": "pull", "equipment": "full_gym", "injury_tags": ["shoulder"], "instructions": "Pull bar to upper chest, control the return, avoid swinging."},
    {"name": "Leg Press", "focus": "lower_body", "equipment": "full_gym", "injury_tags": ["left_knee", "right_knee"], "instructions": "Feet shoulder-width on platform, lower under control, press through heels."},
    {"name": "Seated Cable Row", "focus": "pull", "equipment": "full_gym", "injury_tags": ["lower_back"], "instructions": "Pull handle to torso keeping back straight, squeeze shoulder blades."},
    {"name": "Leg Curl Machine", "focus": "lower_body", "equipment": "full_gym", "injury_tags": ["left_knee", "right_knee"], "instructions": "Curl pad toward glutes with control, avoid hips lifting off pad."},
    {"name": "Cable Triceps Pushdown", "focus": "push", "equipment": "full_gym", "injury_tags": ["shoulder"], "instructions": "Push bar down keeping elbows pinned at sides."},
    {"name": "Treadmill Intervals", "focus": "cardio", "equipment": "full_gym", "injury_tags": ["ankle"], "instructions": "Alternate 30s fast pace with 90s recovery pace."},
    {"name": "Rowing Machine", "focus": "cardio", "equipment": "full_gym", "injury_tags": ["lower_back"], "instructions": "Drive with legs first, then pull with arms, reverse the sequence to return."},
]


def exercises_for(focus: str, equipment_access: str, exclude_injury_tags: set[str]) -> list[dict]:
    max_tier = EQUIPMENT_TIER.get(equipment_access, 0)
    return [
        ex
        for ex in EXERCISES
        if ex["focus"] == focus
        and EQUIPMENT_TIER.get(ex["equipment"], 0) <= max_tier
        and not (set(ex["injury_tags"]) & exclude_injury_tags)
    ]
