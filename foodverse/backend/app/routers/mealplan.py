from fastapi import APIRouter
from pydantic import BaseModel, Field

from app import db, scoring
from app.llm import ask_json

router = APIRouter(prefix="/api/mealplan", tags=["mealplan"])

SYSTEM = """You are a registered-dietitian-style meal planner. Build the plan around the FIXED daily
targets given in the request (each day's meals should total close to the calorie target).
Never include an allergen or disliked food, including as a swap option. If recent intake is provided, adjust
the plan to correct imbalances (e.g. low protein, high calories) and explain how in "notes".
Every meal must have a one-line "why" tied to the person's goal. Schema:
{"daily_targets": {"calories": number, "protein_g": number, "carbs_g": number, "fat_g": number},
 "days": [{"day": str, "meals": [{"type": "Breakfast"|"Lunch"|"Snack"|"Dinner", "name": str,
   "calories": number, "protein_g": number, "description": str, "why": str,
   "alternatives": [{"name": str, "calories": number, "protein_g": number}]}],
   "total_calories": number}],
 "grocery_list": [str], "notes": [str], "weekly_summary": str,
 "disclaimer": "General guidance, not medical advice."}"""


class Profile(BaseModel):
    age: int = Field(ge=10, le=100)
    sex: str
    height_cm: float = Field(gt=50, lt=260)
    weight_kg: float = Field(gt=20, lt=400)
    activity: str = "moderate"      # sedentary | light | moderate | active
    goal: str = "maintain"          # lose | maintain | gain
    diet: str = "no restriction"    # vegetarian, vegan, keto, ...
    allergies: str = ""
    dislikes: str = ""
    days: int = Field(default=3, ge=1, le=7)
    use_history: bool = False       # feed meals scanned in the Meal scan module into the plan


@router.post("/generate")
def generate(p: Profile):
    t = scoring.targets(p.model_dump())
    text = p.model_dump_json(exclude={"use_history"}, indent=2)
    text += (f"\n\nFIXED daily targets: {t['calories']} kcal, {t['protein_g']} g protein, "
             f"{t['carbs_g']} g carbs, {t['fat_g']} g fat. Give 1 or 2 alternatives per meal.")
    if p.use_history:
        s = db.summary(7)
        if s["meal_count"]:
            text += (f"\n\nRecent intake (last 7 days, from scanned meals): {s['meal_count']} meals, "
                     f"{s['total_calories']} kcal, {s['total_protein_g']} g protein, "
                     f"{s['total_carbs_g']} g carbs, {s['total_fat_g']} g fat, "
                     f"avg health score {s['avg_health_score']}. Dishes: {', '.join(s['recent_dishes'])}.")
    plan = ask_json(SYSTEM, [{"type": "text", "text": text}], max_tokens=4000)
    plan["daily_targets"] = {k: t[k] for k in ("calories", "protein_g", "carbs_g", "fat_g")}
    plan["energy_estimate"] = {"bmr": t["bmr"], "tdee": t["tdee"]}
    plan["allergen_warnings"] = scoring.allergen_warnings(plan, p.allergies + "," + p.dislikes)
    return plan
