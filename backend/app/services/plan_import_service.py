"""
Orchestration layer for Sprint 5 plan import: creating ImportedPlan rows,
running comparison + AI analysis (Feature 3/4/5), and applying a decision
(Feature 6: use mine / merge / use EvoFit). Kept separate from the parsers
and the comparison/analysis engines so each stays independently testable.
"""
from datetime import date

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.plan_import import ImportedPlan, PlanAnalysis
from app.models.workout import WorkoutPlan
from app.models.nutrition import NutritionPlan
from app.services import workout_service, nutrition_service, workout_preferences_service, nutrition_preferences_service
from app.services import week_utils
from app.services.workout_plan_parser import parse_workout_text
from app.services.nutrition_plan_parser import parse_nutrition_text
from app.services.plan_comparison_service import compare_workout_plans, compare_nutrition_plans
from app.services.plan_analysis_service import analyze_workout, analyze_nutrition


def create_imported_plan(
    db: Session, user: User, plan_type: str, plan_name: str, source_type: str, raw_text: str
) -> ImportedPlan:
    if plan_type == "workout":
        parsed_data = parse_workout_text(raw_text)
    else:
        parsed_data = parse_nutrition_text(raw_text)

    record = ImportedPlan(
        user_id=user.id,
        plan_type=plan_type,
        plan_name=plan_name.strip() or f"Imported {plan_type} plan",
        source_type=source_type,
        raw_text=raw_text,
        parsed_data=parsed_data,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_imported_plan(db: Session, user: User, imported_plan_id: str) -> ImportedPlan | None:
    return (
        db.query(ImportedPlan)
        .filter(ImportedPlan.id == imported_plan_id, ImportedPlan.user_id == user.id)
        .first()
    )


def list_imported_plans(db: Session, user: User, plan_type: str | None = None) -> list[ImportedPlan]:
    query = db.query(ImportedPlan).filter(ImportedPlan.user_id == user.id)
    if plan_type:
        query = query.filter(ImportedPlan.plan_type == plan_type)
    return query.order_by(ImportedPlan.created_at.desc()).all()


def delete_imported_plan(db: Session, user: User, imported_plan_id: str) -> bool:
    record = get_imported_plan(db, user, imported_plan_id)
    if record is None:
        return False
    db.query(PlanAnalysis).filter(PlanAnalysis.imported_plan_id == record.id).delete()
    db.delete(record)
    db.commit()
    return True


def _current_evofit_workout_plan(db: Session, user: User) -> WorkoutPlan | None:
    try:
        return workout_service.get_or_create_current_plan(db, user)
    except Exception:
        return None


def run_comparison(db: Session, user: User, imported_plan: ImportedPlan) -> PlanAnalysis:
    if imported_plan.plan_type == "workout":
        evofit_plan = _current_evofit_workout_plan(db, user)
        comparison = compare_workout_plans(imported_plan.parsed_data, evofit_plan)
        observations, suggestions = analyze_workout(comparison, imported_plan.parsed_data)
    else:
        week_start = week_utils.week_start(date.today())
        evofit_plan = nutrition_service.get_plan_for_week(db, user, week_start)
        comparison = compare_nutrition_plans(imported_plan.parsed_data, evofit_plan)
        observations, suggestions = analyze_nutrition(comparison, imported_plan.parsed_data)

    effectiveness_score = {
        "mine": comparison["mine"]["effectiveness_score"],
        "evofit": comparison["evofit"]["effectiveness_score"] if comparison.get("evofit") else None,
    }

    analysis = PlanAnalysis(
        imported_plan_id=imported_plan.id,
        user_id=user.id,
        comparison=comparison,
        observations=observations,
        suggestions=suggestions,
        effectiveness_score=effectiveness_score,
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis


def get_latest_analysis(db: Session, user: User, imported_plan_id: str) -> PlanAnalysis | None:
    return (
        db.query(PlanAnalysis)
        .filter(PlanAnalysis.imported_plan_id == imported_plan_id, PlanAnalysis.user_id == user.id)
        .order_by(PlanAnalysis.created_at.desc())
        .first()
    )


# --- Feature 6: apply a decision -------------------------------------------------


def _imported_workout_to_schedule(parsed_data: dict) -> list[dict]:
    """Converts parser output into the WorkoutPlan.schedule shape so an
    imported plan can become the user's active plan directly ('Use My Plan')."""
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    by_index = {i: None for i in range(7)}
    for i, day in enumerate(parsed_data["days"][:7]):
        exercises = [
            {
                "name": ex["name"],
                "sets": ex["sets"] or 3,
                "reps": ex["reps"] or "8-12",
                "rest_seconds": 60,
                "instructions": "Imported from your uploaded plan.",
            }
            for ex in day["exercises"]
        ]
        by_index[i] = {
            "day_name": day_order[i] if i < len(day_order) else day["day_name"],
            "is_rest_day": day["is_rest_day"] or not exercises,
            "focus": "imported",
            "exercises": exercises,
            "estimated_duration_minutes": len(exercises) * 6,
        }
    schedule = []
    for i in range(7):
        schedule.append(by_index[i] or {
            "day_name": day_order[i], "is_rest_day": True, "focus": "rest",
            "exercises": [], "estimated_duration_minutes": 0,
        })
    return schedule


def _imported_nutrition_to_days(parsed_data: dict) -> list[dict]:
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    days = []
    for i in range(7):
        if i < len(parsed_data["days"]):
            src = parsed_data["days"][i]
            meals = [
                {"meal_type": m["meal_type"], "name": m["name"], "calories": m["calories"],
                 "protein_g": m["protein_g"], "carbs_g": m["carbs_g"], "fat_g": m["fat_g"]}
                for m in src["meals"]
            ]
            days.append({
                "day_name": day_order[i],
                "date": None,
                "target_calories": src["total_calories"] or parsed_data["avg_daily_calories"],
                "target_protein_g": src["total_protein_g"] or parsed_data["avg_daily_protein_g"],
                "target_carbs_g": src["total_carbs_g"] or parsed_data["avg_daily_carbs_g"],
                "target_fat_g": src["total_fat_g"] or parsed_data["avg_daily_fat_g"],
                "water_goal_ml": parsed_data.get("avg_water_ml") or 2000,
                "meals": meals,
            })
        else:
            days.append({
                "day_name": day_order[i], "date": None,
                "target_calories": parsed_data["avg_daily_calories"],
                "target_protein_g": parsed_data["avg_daily_protein_g"],
                "target_carbs_g": parsed_data["avg_daily_carbs_g"],
                "target_fat_g": parsed_data["avg_daily_fat_g"],
                "water_goal_ml": parsed_data.get("avg_water_ml") or 2000,
                "meals": [],
            })
    return days


def apply_decision(db: Session, user: User, imported_plan: ImportedPlan, mode: str) -> dict:
    """mode: 'use_mine' | 'merge' | 'use_evofit'"""
    if mode not in ("use_mine", "merge", "use_evofit"):
        raise ValueError("mode must be one of: use_mine, merge, use_evofit")

    week_start = week_utils.week_start(date.today())
    result: dict = {"mode": mode, "plan_type": imported_plan.plan_type}

    if imported_plan.plan_type == "workout":
        if mode == "use_mine":
            schedule = _imported_workout_to_schedule(imported_plan.parsed_data)
            plan = WorkoutPlan(
                user_id=user.id,
                week_start_date=week_start,
                schedule=schedule,
                generation_basis={"source": "user_import", "imported_plan_id": imported_plan.id},
            )
            db.add(plan)
            db.commit()
            db.refresh(plan)
            result["workout_plan_id"] = plan.id
        elif mode == "merge":
            prefs = workout_preferences_service.get_or_create_preferences(db, user)
            matched_names = {
                ex["matched_library_name"]
                for d in imported_plan.parsed_data["days"]
                for ex in d["exercises"]
                if ex["matched_library_name"]
            }
            liked = set(prefs.liked_exercises or [])
            liked |= matched_names
            prefs.liked_exercises = list(liked)[:40]
            db.add(prefs)
            db.commit()
            plan = workout_service.regenerate_current_plan(db, user)
            result["workout_plan_id"] = plan.id
        else:  # use_evofit
            plan = workout_service.get_or_create_current_plan(db, user)
            result["workout_plan_id"] = plan.id
    else:
        if mode == "use_mine":
            days = _imported_nutrition_to_days(imported_plan.parsed_data)
            plan = NutritionPlan(
                user_id=user.id,
                week_start_date=week_start,
                days=days,
                generation_basis={"source": "user_import", "imported_plan_id": imported_plan.id},
            )
            db.add(plan)
            db.commit()
            db.refresh(plan)
            result["nutrition_plan_id"] = plan.id
        elif mode == "merge":
            prefs = nutrition_preferences_service.get_or_create_preferences(db, user)
            matched_names = {
                m["name"] for d in imported_plan.parsed_data["days"] for m in d["meals"] if not m["is_estimated"]
            } | {
                m["name"] for d in imported_plan.parsed_data["days"] for m in d["meals"]
            }
            favorites = set(prefs.favorite_foods or [])
            favorites |= matched_names
            prefs.favorite_foods = list(favorites)[:40]
            if imported_plan.parsed_data.get("avg_water_ml") and (
                not prefs.water_goal_ml or imported_plan.parsed_data["avg_water_ml"] > prefs.water_goal_ml
            ):
                prefs.water_goal_ml = round(imported_plan.parsed_data["avg_water_ml"])
            db.add(prefs)
            db.commit()
            plan = nutrition_service.regenerate_plan_for_week(db, user, week_start)
            result["nutrition_plan_id"] = plan.id
        else:  # use_evofit
            plan = nutrition_service.get_plan_for_week(db, user, week_start) or nutrition_service.regenerate_plan_for_week(db, user, week_start)
            result["nutrition_plan_id"] = plan.id

    imported_plan.applied_status = {"use_mine": "used_mine", "merge": "merged", "use_evofit": "used_evofit"}[mode]
    db.add(imported_plan)
    db.commit()
    return result
