"""
Lightweight dev-only schema guard.

This project has no migration framework (no Alembic) and relies entirely on
Base.metadata.create_all(), which never alters existing tables. Sprint 2
changed NutritionPlan from a daily shape to a weekly shape mirroring
WorkoutPlan (see SPRINT_2_README.md), so a SQLite file created before this
change has an incompatible `nutrition_plans` table (old columns like
`plan_date`, `target_calories`, `meals` at the top level).

Since this is local development data for a capstone project (no production
deployment), we detect the old shape and drop the two affected tables so
`create_all` recreates them fresh in the new shape. Every other table
(users, onboarding_profiles, medical_history, workout_plans, ...) is left
untouched. If a real migration tool is introduced later, this module can be
deleted in favor of a proper migration.
"""
from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine


def reset_incompatible_nutrition_tables(engine: Engine) -> None:
    inspector = inspect(engine)
    if "nutrition_plans" not in inspector.get_table_names():
        return

    columns = {col["name"] for col in inspector.get_columns("nutrition_plans")}
    is_old_daily_shape = "week_start_date" not in columns

    if not is_old_daily_shape:
        return

    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS meal_completions"))
        conn.execute(text("DROP TABLE IF EXISTS nutrition_plans"))
