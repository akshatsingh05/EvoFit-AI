"""
Meal library. Each entry has base macros for a standard serving; the
generator scales portions to hit the day's calorie targets. Not a fixed
meal plan — a pool filtered by diet type and allergies, then selected from
(with per-user/per-regeneration variety, not always the first match).

`low_glycemic` is a soft preference tag (True = relatively higher protein/fat,
lower rapid-carb content) used to nudge meal choice for users with
diabetes-related conditions logged in their medical history — it is not a
hard filter, so it can never empty a pool.
"""

MEALS = {
    "breakfast": [
        {"name": "Greek Yogurt with Berries and Granola", "diet_types": ["omnivore", "vegetarian", "pescatarian"], "allergens": ["dairy", "gluten"], "calories": 350, "protein_g": 22, "carbs_g": 45, "fat_g": 9, "low_glycemic": False},
        {"name": "Veggie Scramble with Whole Grain Toast", "diet_types": ["omnivore", "vegetarian", "pescatarian"], "allergens": ["eggs", "gluten"], "calories": 380, "protein_g": 24, "carbs_g": 35, "fat_g": 16, "low_glycemic": False},
        {"name": "Tofu Scramble with Spinach", "diet_types": ["vegan", "vegetarian"], "allergens": ["soy"], "calories": 320, "protein_g": 20, "carbs_g": 22, "fat_g": 16, "low_glycemic": True},
        {"name": "Overnight Oats with Almond Butter", "diet_types": ["vegan", "vegetarian", "omnivore", "pescatarian"], "allergens": ["nuts", "gluten"], "calories": 400, "protein_g": 14, "carbs_g": 55, "fat_g": 14, "low_glycemic": False},
        {"name": "Smoked Salmon and Avocado Toast", "diet_types": ["pescatarian", "omnivore"], "allergens": ["fish", "gluten"], "calories": 420, "protein_g": 26, "carbs_g": 32, "fat_g": 20, "low_glycemic": False},
        {"name": "Bulletproof-Style Eggs and Bacon", "diet_types": ["keto", "omnivore"], "allergens": ["eggs"], "calories": 450, "protein_g": 28, "carbs_g": 4, "fat_g": 34, "low_glycemic": True},
        {"name": "Protein Smoothie Bowl", "diet_types": ["omnivore", "vegetarian", "pescatarian", "other"], "allergens": ["dairy"], "calories": 360, "protein_g": 30, "carbs_g": 40, "fat_g": 8, "low_glycemic": False},
        {"name": "Cottage Cheese and Veggie Bowl", "diet_types": ["omnivore", "vegetarian", "pescatarian"], "allergens": ["dairy"], "calories": 300, "protein_g": 28, "carbs_g": 14, "fat_g": 12, "low_glycemic": True},
        {"name": "Chia Seed Pudding with Berries", "diet_types": ["vegan", "vegetarian", "omnivore", "pescatarian"], "allergens": [], "calories": 340, "protein_g": 12, "carbs_g": 38, "fat_g": 16, "low_glycemic": True},
        {"name": "Breakfast Burrito with Black Beans", "diet_types": ["vegetarian", "omnivore"], "allergens": ["eggs", "gluten"], "calories": 430, "protein_g": 22, "carbs_g": 48, "fat_g": 16, "low_glycemic": False},
    ],
    "lunch": [
        {"name": "Grilled Chicken and Quinoa Bowl", "diet_types": ["omnivore"], "allergens": [], "calories": 520, "protein_g": 42, "carbs_g": 48, "fat_g": 14, "low_glycemic": False},
        {"name": "Chickpea and Feta Salad", "diet_types": ["vegetarian", "omnivore", "pescatarian"], "allergens": ["dairy"], "calories": 480, "protein_g": 22, "carbs_g": 50, "fat_g": 18, "low_glycemic": False},
        {"name": "Lentil and Vegetable Curry with Rice", "diet_types": ["vegan", "vegetarian"], "allergens": [], "calories": 520, "protein_g": 20, "carbs_g": 78, "fat_g": 10, "low_glycemic": False},
        {"name": "Seared Tuna Poke Bowl", "diet_types": ["pescatarian", "omnivore"], "allergens": ["fish", "soy"], "calories": 500, "protein_g": 36, "carbs_g": 52, "fat_g": 14, "low_glycemic": False},
        {"name": "Turkey Lettuce Wraps", "diet_types": ["omnivore", "keto"], "allergens": [], "calories": 400, "protein_g": 34, "carbs_g": 12, "fat_g": 22, "low_glycemic": True},
        {"name": "Zucchini Noodles with Ground Beef", "diet_types": ["keto", "omnivore"], "allergens": [], "calories": 460, "protein_g": 32, "carbs_g": 10, "fat_g": 30, "low_glycemic": True},
        {"name": "Tempeh and Vegetable Stir-Fry", "diet_types": ["vegan", "vegetarian"], "allergens": ["soy"], "calories": 470, "protein_g": 26, "carbs_g": 46, "fat_g": 16, "low_glycemic": False},
        {"name": "Grilled Salmon Salad", "diet_types": ["pescatarian", "omnivore"], "allergens": ["fish"], "calories": 490, "protein_g": 38, "carbs_g": 20, "fat_g": 28, "low_glycemic": True},
        {"name": "Black Bean and Sweet Potato Bowl", "diet_types": ["vegan", "vegetarian"], "allergens": [], "calories": 500, "protein_g": 18, "carbs_g": 82, "fat_g": 10, "low_glycemic": False},
        {"name": "Chicken Caesar Salad (light dressing)", "diet_types": ["omnivore"], "allergens": ["dairy", "gluten"], "calories": 450, "protein_g": 38, "carbs_g": 18, "fat_g": 24, "low_glycemic": True},
    ],
    "snack": [
        {"name": "Apple with Peanut Butter", "diet_types": ["omnivore", "vegetarian", "vegan", "pescatarian"], "allergens": ["nuts"], "calories": 220, "protein_g": 7, "carbs_g": 24, "fat_g": 12, "low_glycemic": False},
        {"name": "Cottage Cheese with Pineapple", "diet_types": ["omnivore", "vegetarian", "pescatarian"], "allergens": ["dairy"], "calories": 180, "protein_g": 18, "carbs_g": 18, "fat_g": 3, "low_glycemic": False},
        {"name": "Hummus with Carrot Sticks", "diet_types": ["vegan", "vegetarian", "omnivore", "pescatarian"], "allergens": [], "calories": 200, "protein_g": 7, "carbs_g": 22, "fat_g": 9, "low_glycemic": False},
        {"name": "Mixed Nuts", "diet_types": ["keto", "vegan", "vegetarian", "omnivore", "pescatarian"], "allergens": ["nuts"], "calories": 210, "protein_g": 6, "carbs_g": 7, "fat_g": 18, "low_glycemic": True},
        {"name": "Protein Shake", "diet_types": ["omnivore", "vegetarian", "pescatarian", "other"], "allergens": ["dairy"], "calories": 180, "protein_g": 25, "carbs_g": 8, "fat_g": 4, "low_glycemic": True},
        {"name": "Rice Cakes with Avocado", "diet_types": ["vegan", "vegetarian", "omnivore", "pescatarian"], "allergens": [], "calories": 190, "protein_g": 4, "carbs_g": 24, "fat_g": 9, "low_glycemic": False},
        {"name": "Hard-Boiled Eggs", "diet_types": ["omnivore", "vegetarian", "pescatarian", "keto"], "allergens": ["eggs"], "calories": 150, "protein_g": 13, "carbs_g": 1, "fat_g": 10, "low_glycemic": True},
        {"name": "Edamame with Sea Salt", "diet_types": ["vegan", "vegetarian", "omnivore", "pescatarian"], "allergens": ["soy"], "calories": 170, "protein_g": 15, "carbs_g": 12, "fat_g": 7, "low_glycemic": True},
    ],
    "dinner": [
        {"name": "Baked Salmon with Roasted Vegetables", "diet_types": ["pescatarian", "omnivore"], "allergens": ["fish"], "calories": 550, "protein_g": 38, "carbs_g": 30, "fat_g": 26, "low_glycemic": True},
        {"name": "Grilled Steak with Sweet Potato", "diet_types": ["omnivore"], "allergens": [], "calories": 600, "protein_g": 44, "carbs_g": 45, "fat_g": 24, "low_glycemic": False},
        {"name": "Stuffed Bell Peppers with Black Beans", "diet_types": ["vegan", "vegetarian"], "allergens": [], "calories": 480, "protein_g": 18, "carbs_g": 68, "fat_g": 12, "low_glycemic": False},
        {"name": "Shrimp and Vegetable Skewers", "diet_types": ["pescatarian", "omnivore"], "allergens": ["shellfish"], "calories": 420, "protein_g": 36, "carbs_g": 24, "fat_g": 16, "low_glycemic": True},
        {"name": "Herb-Roasted Chicken Thighs with Broccoli", "diet_types": ["omnivore", "keto"], "allergens": [], "calories": 540, "protein_g": 40, "carbs_g": 14, "fat_g": 32, "low_glycemic": True},
        {"name": "Cauliflower Fried Rice with Tofu", "diet_types": ["vegan", "vegetarian", "keto"], "allergens": ["soy"], "calories": 400, "protein_g": 20, "carbs_g": 30, "fat_g": 18, "low_glycemic": True},
        {"name": "Whole Wheat Pasta with Marinara and White Beans", "diet_types": ["vegan", "vegetarian", "omnivore"], "allergens": ["gluten"], "calories": 520, "protein_g": 20, "carbs_g": 88, "fat_g": 8, "low_glycemic": False},
        {"name": "Grilled Cod with Quinoa and Asparagus", "diet_types": ["pescatarian", "omnivore"], "allergens": ["fish"], "calories": 480, "protein_g": 38, "carbs_g": 40, "fat_g": 14, "low_glycemic": False},
        {"name": "Turkey Meatballs with Zucchini Noodles", "diet_types": ["omnivore", "keto"], "allergens": [], "calories": 460, "protein_g": 36, "carbs_g": 16, "fat_g": 26, "low_glycemic": True},
        {"name": "Chickpea and Spinach Curry", "diet_types": ["vegan", "vegetarian"], "allergens": [], "calories": 470, "protein_g": 18, "carbs_g": 62, "fat_g": 14, "low_glycemic": False},
    ],
}

MEAL_CALORIE_SHARE = {"breakfast": 0.25, "lunch": 0.30, "snack": 0.15, "dinner": 0.30}


def meals_for(
    meal_type: str,
    diet_type: str,
    exclude_allergens: set,
    prefer_low_glycemic: bool = False,
) -> list:
    pool = [
        m
        for m in MEALS.get(meal_type, [])
        if diet_type in m["diet_types"] and not (set(m["allergens"]) & exclude_allergens)
    ]
    if prefer_low_glycemic:
        pool = sorted(pool, key=lambda m: 0 if m.get("low_glycemic") else 1)
    return pool
