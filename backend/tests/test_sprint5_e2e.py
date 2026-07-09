import sys, io, json
sys.path.insert(0, '.')

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def check(cond, label):
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {label}")
    if not cond:
        FAILURES.append(label)

FAILURES = []

# --- 1. Signup / Auth (regression) ---
signup_resp = client.post("/auth/signup", json={
    "full_name": "Sprint5 Tester", "email": "sprint5tester@example.com", "password": "TestPass123"
})
check(signup_resp.status_code == 201, f"signup succeeds ({signup_resp.status_code}) {signup_resp.text[:200]}")
token = signup_resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# --- 2. Onboarding (regression, required for plan generation) ---
onboarding_payload = {
    "goals": {"primary_goal": "build_muscle", "target_timeline_weeks": 12, "secondary_goals": []},
    "body_metrics": {"height_cm": 178, "weight_kg": 80, "target_weight_kg": 85, "age": 28, "sex": "male"},
    "fitness_experience": {"experience_level": "intermediate", "workouts_per_week_current": 4,
                             "preferred_workout_types": ["strength"], "equipment_access": "full_gym"},
    "lifestyle_diet": {"diet_type": "omnivore", "meals_per_day": 4, "sleep_hours_avg": 7.5,
                        "stress_level": "moderate", "occupation_activity": "light"},
}
ob_resp = client.post("/onboarding", json=onboarding_payload, headers=headers)
check(ob_resp.status_code == 200, f"onboarding save ({ob_resp.status_code}) {ob_resp.text[:200]}")

med_resp = client.post("/medical-history", json={
    "conditions": [], "injuries": [], "medications": None, "allergies": None,
    "additional_notes": None, "cleared_for_exercise": True
}, headers=headers)
check(med_resp.status_code == 200, f"medical history save ({med_resp.status_code}) {med_resp.text[:200]}")

# --- 3. Baseline regression: dashboard / workout / nutrition / progress / settings / notifications ---
for path in ["/dashboard", "/workout", "/nutrition", "/progress", "/settings", "/notifications", "/profile"]:
    r = client.get(path, headers=headers)
    check(r.status_code == 200, f"GET {path} ({r.status_code}) {r.text[:150] if r.status_code != 200 else ''}")

# --- 4. Sprint 5 Feature 1: import workout plan (manual text) ---
workout_text = """Monday
Bench Press 4x8
Incline Dumbbell Press 3x10
Cable Fly 3x12

Tuesday
Deadlift 3x5
Barbell Row 4x8
Lat Pulldown 3x10

Wednesday
Rest

Thursday
Squat 4x8
Leg Press 3x10
Calf Raise 3x15

Friday
Overhead Press 3x8
Lateral Raise 3x12
Bicep Curl 3x10
"""
imp_resp = client.post("/plan-import/workout/manual", headers=headers, json={
    "plan_name": "My Custom Split", "raw_text": workout_text
})
check(imp_resp.status_code == 200, f"import workout manual ({imp_resp.status_code}) {imp_resp.text[:300]}")
workout_import = imp_resp.json()
check(workout_import["parsed_data"]["workout_days_count"] == 4, "parsed 4 workout days")
workout_import_id = workout_import["id"]

# --- 5. Feature 1: import workout plan via TXT file ---
txt_bytes = workout_text.encode("utf-8")
file_resp = client.post(
    "/plan-import/workout/file", headers=headers,
    data={"plan_name": "Uploaded TXT Plan"},
    files={"file": ("plan.txt", io.BytesIO(txt_bytes), "text/plain")},
)
check(file_resp.status_code == 200, f"import workout txt file ({file_resp.status_code}) {file_resp.text[:300]}")

# --- 6. Feature 1: import via DOCX ---
import docx
doc = docx.Document()
for line in workout_text.splitlines():
    doc.add_paragraph(line)
docx_buf = io.BytesIO()
doc.save(docx_buf)
docx_buf.seek(0)
docx_resp = client.post(
    "/plan-import/workout/file", headers=headers,
    data={"plan_name": "Uploaded DOCX Plan"},
    files={"file": ("plan.docx", docx_buf, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
)
check(docx_resp.status_code == 200, f"import workout docx file ({docx_resp.status_code}) {docx_resp.text[:300]}")

# --- 7. Feature 1: import via PDF ---
from reportlab.pdfgen import canvas
pdf_buf = io.BytesIO()
c = canvas.Canvas(pdf_buf)
y = 800
for line in workout_text.splitlines():
    c.drawString(50, y, line)
    y -= 15
    if y < 50:
        c.showPage()
        y = 800
c.save()
pdf_buf.seek(0)
pdf_resp = client.post(
    "/plan-import/workout/file", headers=headers,
    data={"plan_name": "Uploaded PDF Plan"},
    files={"file": ("plan.pdf", pdf_buf, "application/pdf")},
)
check(pdf_resp.status_code == 200, f"import workout pdf file ({pdf_resp.status_code}) {pdf_resp.text[:300]}")
check(pdf_resp.json()["parsed_data"]["workout_days_count"] >= 3, "PDF-parsed plan has training days")

# --- 8. Feature 1: import via Image (OCR) ---
from PIL import Image, ImageDraw, ImageFont
img = Image.new("RGB", (800, 1000), color="white")
draw = ImageDraw.Draw(img)
y = 10
for line in workout_text.splitlines():
    draw.text((10, y), line, fill="black")
    y += 20
img_buf = io.BytesIO()
img.save(img_buf, format="PNG")
img_buf.seek(0)
img_resp = client.post(
    "/plan-import/workout/file", headers=headers,
    data={"plan_name": "Uploaded Image Plan"},
    files={"file": ("plan.png", img_buf, "image/png")},
)
check(img_resp.status_code == 200, f"import workout image(OCR) file ({img_resp.status_code}) {img_resp.text[:300]}")
ocr_days = img_resp.json()["parsed_data"]["workout_days_count"]
print(f"    OCR detected {ocr_days} workout day(s) (OCR accuracy varies)")

# --- 9. Feature 2: import nutrition plan (manual) ---
nutrition_text = """Monday
Breakfast
Oatmeal with banana - 350 calories, 12g protein, 60g carbs, 6g fat
Lunch
Grilled Chicken and Quinoa Bowl
Snack
Apple with Peanut Butter
Dinner
Salmon with rice - 500 cal 40g protein
Water: 2 liters

Tuesday
Breakfast
Greek Yogurt with Berries and Granola
Lunch
Chicken Caesar Salad
Dinner
Turkey Lettuce Wraps
Water: 1500ml
"""
nut_resp = client.post("/plan-import/nutrition/manual", headers=headers, json={
    "plan_name": "My Diet Plan", "raw_text": nutrition_text
})
check(nut_resp.status_code == 200, f"import nutrition manual ({nut_resp.status_code}) {nut_resp.text[:300]}")
nutrition_import = nut_resp.json()
nutrition_import_id = nutrition_import["id"]
check(nutrition_import["parsed_data"]["total_meals"] > 0, "parsed nutrition meals")

# --- 10. Feature 3/4/5: compare + AI analysis + suggestions (workout) ---
cmp_resp = client.post(f"/plan-import/{workout_import_id}/compare", headers=headers)
check(cmp_resp.status_code == 200, f"compare workout plan ({cmp_resp.status_code}) {cmp_resp.text[:400]}")
analysis = cmp_resp.json()
check(len(analysis["observations"]) > 0, "workout analysis produced observations")
check(isinstance(analysis["suggestions"], list), "workout analysis produced suggestions list")
print(f"    Observations: {analysis['observations'][:2]}")
print(f"    Suggestions: {[s['title'] for s in analysis['suggestions'][:3]]}")

# --- 11. Compare nutrition ---
ncmp_resp = client.post(f"/plan-import/{nutrition_import_id}/compare", headers=headers)
check(ncmp_resp.status_code == 200, f"compare nutrition plan ({ncmp_resp.status_code}) {ncmp_resp.text[:400]}")
nanalysis = ncmp_resp.json()
check(len(nanalysis["observations"]) > 0, "nutrition analysis produced observations")
print(f"    Nutrition observations: {nanalysis['observations'][:2]}")

# --- 12. Feature 7: History ---
hist_resp = client.get("/plan-import/history", headers=headers)
check(hist_resp.status_code == 200, f"get import history ({hist_resp.status_code})")
check(len(hist_resp.json()["entries"]) >= 6, f"history has all imports ({len(hist_resp.json()['entries'])} entries)")

hist_workout_resp = client.get("/plan-import/history?plan_type=workout", headers=headers)
check(hist_workout_resp.status_code == 200 and len(hist_workout_resp.json()["entries"]) >= 5, "history filters by plan_type")

# --- 13. Feature 6: apply decisions (use_mine, merge, use_evofit) ---
apply_mine = client.post(f"/plan-import/{workout_import_id}/apply", headers=headers, json={"mode": "use_mine"})
check(apply_mine.status_code == 200, f"apply use_mine (workout) ({apply_mine.status_code}) {apply_mine.text[:300]}")
check(apply_mine.json().get("workout_plan_id") is not None, "use_mine created a workout plan id")

apply_merge = client.post(f"/plan-import/{nutrition_import_id}/apply", headers=headers, json={"mode": "merge"})
check(apply_merge.status_code == 200, f"apply merge (nutrition) ({apply_merge.status_code}) {apply_merge.text[:300]}")

file_import_id = file_resp.json()["id"]
apply_evofit = client.post(f"/plan-import/{file_import_id}/apply", headers=headers, json={"mode": "use_evofit"})
check(apply_evofit.status_code == 200, f"apply use_evofit (workout) ({apply_evofit.status_code}) {apply_evofit.text[:300]}")

# --- 14. Feature 8: Export PDF/DOCX ---
export_pdf = client.get(f"/plan-import/{workout_import_id}/export?format=pdf", headers=headers)
check(export_pdf.status_code == 200 and export_pdf.headers["content-type"] == "application/pdf", f"export workout PDF ({export_pdf.status_code})")
check(len(export_pdf.content) > 500, "PDF export has real content")

export_docx = client.get(f"/plan-import/{nutrition_import_id}/export?format=docx", headers=headers)
check(export_docx.status_code == 200, f"export nutrition DOCX ({export_docx.status_code})")
check(len(export_docx.content) > 500, "DOCX export has real content")

export_combined = client.get("/plan-import/export/combined?format=pdf", headers=headers)
check(export_combined.status_code == 200, f"export combined report ({export_combined.status_code}) {export_combined.text[:200] if export_combined.status_code!=200 else ''}")

# --- 15. Post-Sprint5 regression: verify existing flows still work after applying imported plans ---
for path in ["/dashboard", "/workout", "/nutrition", "/progress", "/settings", "/workout/week", "/nutrition/week"]:
    r = client.get(path, headers=headers)
    check(r.status_code == 200, f"post-import regression GET {path} ({r.status_code}) {r.text[:150] if r.status_code!=200 else ''}")

regen_resp = client.post("/workout/regenerate", headers=headers)
check(regen_resp.status_code == 200, f"workout regenerate still works ({regen_resp.status_code})")

# --- 16. Delete account regression (final) ---
# Use a separate throwaway account so we don't lose the one we've been testing with mid-suite
signup2 = client.post("/auth/signup", json={"full_name": "Delete Tester", "email": "deletetester5@example.com", "password": "TestPass123"})
del_headers = {"Authorization": f"Bearer {signup2.json()['access_token']}"}
del_resp = client.delete("/profile/account", headers=del_headers)
check(del_resp.status_code in (200, 204), f"delete account still works ({del_resp.status_code}) {del_resp.text[:200]}")

print("\n" + "="*60)
if FAILURES:
    print(f"{len(FAILURES)} FAILURE(S):")
    for f in FAILURES:
        print(" -", f)
    sys.exit(1)
else:
    print("ALL TESTS PASSED")
