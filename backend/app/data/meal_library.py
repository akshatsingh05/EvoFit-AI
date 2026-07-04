"""
Meal library. Each entry has base macros for a standard serving; the
generator scales portions to hit the day's calorie targets. Not a fixed
meal plan — a pool filtered by diet type and allergies, then selected from.
"""

MEALS = {
    "breakfast": [
        {"name": "Greek Yogurt with Berries and Granola", "diet_types": ["omnivore", "vegetarian", "pescatarian"], "allergens": ["dairy", "gluten"], "calories": 350, "protein_g": 22, "carbs_g": 45, "fat_g": 9},
        {"name": "Veggie Scramble with Whole Grain Toast", "diet_types": ["omnivore", "vegetarian", "pescatarian"], "allergens": ["eggs", "gluten"], "calories": 380, "protein_g": 24, "carbs_g": 35, "fat_g": 16},
        {"name": "Tofu Scramble with Spinach", "diet_types": ["vegan", "vegetarian"], "allergens": ["soy"], "calories": 320, "protein_g": 20, "carbs_g": 22, "fat_g": 16},
        {"name": "Overnight Oats with Almond Butter", "diet_types": ["vegan", "vegetarian", "omnivore", "pescatarian"], "allergens": ["nuts", "gluten"], "calories": 400, "protein_g": 14, "carbs_g": 55, "fat_g": 14},
        {"name": "Smoked Salmon and Avocado Toast", "diet_types": ["pescatarian", "omnivore"], "allergens": ["fish", "gluten"], "calories": 420, "protein_g": 26, "carbs_g": 32, "fat_g": 20},
        {"name": "Bulletproof-Style Eggs and Bacon", "diet_types": ["keto", "omnivore"], "allergens": ["eggs"], "calories": 450, "protein_g": 28, "carbs_g": 4, "fat_g": 34},
        {"name": "Protein Smoothie Bowl", "diet_types": ["omnivore", "vegetarian", "pescatarian", "other"], "allergens": ["dairy"], "calories": 360, "protein_g": 30, "carbs_g": 40, "fat_g": 8},
    ],
    "lunch": [
        {"name": "Grilled Chicken and Quinoa Bowl", "diet_types": ["omnivore"], "allergens": [], "calories": 520, "protein_g": 42, "carbs_g": 48, "fat_g": 14},
        {"name": "Chickpea and Feta Salad", "diet_types": ["vegetarian", "omnivore", "pescatarian"], "allergens": ["dairy"], "calories": 480, "protein_g": 22, "carbs_g": 50, "fat_g": 18},
        {"name": "Lentil and Vegetable Curry with Rice", "diet_types": ["vegan", "vegetarian"], "allergens": [], "calories": 520, "protein_g": 20, "carbs_g": 78, "fat_g": 10},
        {"name": "Seared Tuna Poke Bowl", "diet_types": ["pescatarian", "omnivore"], "allergens": ["fish", "soy"], "calories": 500, "protein_g": 36, "carbs_g": 52, "fat_g": 14},
        {"name": "Turkey Lettuce Wraps", "diet_types": ["omnivore", "keto"], "allergens": [], "calories": 400, "protein_g": 34, "carbs_g": 12, "fat_g": 22},
        {"name": "Zucchini Noodles with Ground Beef", "diet_types": ["keto", "omnivore"], "allergens": [], "calories": 460, "protein_g": 32, "carbs_g": 10, "fat_g": 30},
        {"name": "Tempeh and Vegetable Stir-Fry", "diet_types": ["vegan", "vegetarian"], "allergens": ["soy"], "calories": 470, "protein_g": 26, "carbs_g": 46, "fat_g": 16},
    ],
    "snack": [
        {"name": "Apple with Peanut Butter", "diet_types": ["omnivore", "vegetarian", "vegan", "pescatarian"], "allergens": ["nuts"], "calories": 220, "protein_g": 7, "carbs_g": 24, "fat_g": 12},
        {"name": "Cottage Cheese with Pineapple", "diet_types": ["omnivore", "vegetarian", "pescatarian"], "allergens": ["dairy"], "calories": 180, "protein_g": 18, "carbs_g": 18, "fat_g": 3},
        {"name": "Hummus with Carrot Sticks", "diet_types": ["vegan", "vegetarian", "omnivore", "pescatarian"], "allergens": [], "calories": 200, "protein_g": 7, "carbs_g": 22, "fat_g": 9},
        {"name": "Mixed Nuts", "diet_types": ["keto", "vegan", "vegetarian", "omnivore", "pescatarian"], "allergens": ["nuts"], "calories": 210, "protein_g": 6, "carbs_g": 7, "fat_g": 18},
        {"name": "Protein Shake", "diet_types": ["omnivore", "vegetarian", "pescatarian", "other"], "allergens": ["dairy"], "calories": 180, "protein_g": 25, "carbs_g": 8, "fat_g": 4},
        {"name": "Rice Cakes with Avocado", "diet_types": ["vegan", "vegetarian", "omnivore", "pescatarian"], "allergens": [], "calories": 190, "protein_g": 4, "carbs_g": 24, "fat_g": 9},
    ],
    "dinner": [
        {"name": "Baked Salmon with Roasted Vegetables", "diet_types": ["pescatarian", "omnivore"], "allergens": ["fish"], "calories": 550, "protein_g": 38, "carbs_g": 30, "fat_g": 26},
        {"name": "Grilled Steak with Sweet Potato", "diet_types": ["omnivore"], "allergens": [], "calories": 600, "protein_g": 44, "carbs_g": 45, "fat_g": 24},
        {"name": "Stuffed Bell Peppers with Black Beans", "diet_types": ["vegan", "vegetarian"], "allergens": [], "calories": 480, "protein_g": 18, "carbs_g": 68, "fat_g": 12},
        {"name": "Shrimp and Vegetable Skewers", "diet_types": ["pescatarian", "omnivore"], "allergens": ["shellfish"], "calories": 420, "protein_g": 36, "carbs_g": 24, "fat_g": 16},
        {"name": "Herb-Roasted Chicken Thighs with Broccoli", "diet_types": ["omnivore", "keto"], "allergens": [], "calories": 540, "protein_g": 40, "carbs_g": 14, "fat_g": 32},
        {"name": "Cauliflower Fried Rice with Tofu", "diet_types": ["vegan", "vegetarian", "keto"], "allergens": ["soy"], "calories": 400, "protein_g": 20, "carbs_g": 30, "fat_g": 18},
        {"name": "Whole Wheat Pasta with Marinara and White Beans", "diet_types": ["vegan", "vegetarian", "omnivore"], "allergens": ["gluten"], "calories": 520, "protein_g": 20, "carbs_g": 88, "fat_g": 8},
    ],
}

MEAL_CALORIE_SHARE = {"breakfast": 0.25, "lunch": 0.30, "snack": 0.15, "dinner": 0.30}


def meals_for(meal_type: str, diet_type: str, exclude_allergens: set[str]) -> list[dict]:
    return [
        m
        for m in MEALS.get(meal_type, [])
        if diet_type in m["diet_types"] and not (set(m["allergens"]) & exclude_allergens)
    ]
