from fastapi import APIRouter, File, HTTPException, UploadFile

from app import db, features, nutrition
from app.llm import ask_json, image_block
from app.utils import prepare_image

router = APIRouter(prefix="/api/food", tags=["food"])

SYSTEM = """You are a nutrition analyst. Identify every food item in the photo and
estimate nutrition for the visible portions. Handle poor lighting, partial occlusion,
mixed plates and any cuisine (including Indian, East Asian, Mediterranean, Western).
Schema:
{"dish": str, "cuisine": str, "items": [{"name": str, "portion": str, "grams": number, "calories": number,
 "protein_g": number, "carbs_g": number, "fat_g": number}],
 "totals": {"calories": number, "protein_g": number, "carbs_g": number, "fat_g": number},
 "health_score": integer 0-100, "health_notes": str, "confidence": "low"|"medium"|"high",
 "disclaimer": "Estimates from a photo; portion sizes may differ."}
If the image has no food, return {"error": "No food detected"}."""


@router.post("/analyze")
async def analyze(file: UploadFile = File(...), log: bool = True):
    """Analyze a meal photo. With log=true (default) the meal is saved for the planner."""
    if not (file.content_type or "").startswith("image/"):
        raise HTTPException(400, "Upload an image file")
    data = prepare_image(await file.read())
    out = ask_json(SYSTEM, [image_block(data), {"type": "text", "text": "Analyze this meal."}])
    if "error" in out:
        raise HTTPException(422, out["error"])
    out = nutrition.reconcile(out)
    out["image_quality"] = features.quality_warnings(features.decode(data))
    out["logged"] = bool(log)
    if log:
        out["meal_id"] = db.add_meal(out)
    return out
