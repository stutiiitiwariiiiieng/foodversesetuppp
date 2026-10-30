from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from app.llm import ask_json, image_block
from app.utils import prepare_image

router = APIRouter(prefix="/api/cooking", tags=["cooking"])

SYSTEM = """You are a patient cooking coach. Given a dish or ingredients, plus optional
constraints, produce a recipe. Schema:
{"title": str, "detected_ingredients": [str], "servings": integer, "prep_minutes": integer, "cook_minutes": integer,
 "ingredients": [{"item": str, "quantity": str}],
 "steps": [{"step": str, "tip": str, "timer_minutes": number|null}],
 "substitutions": [str], "safety_notes": [str]}"""


class CookRequest(BaseModel):
    query: str                      # "paneer butter masala" or "I have eggs, spinach, rice"
    servings: int = 2
    dietary: str = ""               # e.g. "vegetarian, no onion/garlic"
    skill: str = "beginner"
    question: str = ""              # follow-up, e.g. "sauce is too thick"


@router.post("/recipe")
def recipe(req: CookRequest):
    text = (f"Request: {req.query}\nServings: {req.servings}\nDietary: {req.dietary or 'none'}\n"
            f"Skill level: {req.skill}")
    if req.question:
        text += f"\nCooking problem to address in tips: {req.question}"
    return ask_json(SYSTEM, [{"type": "text", "text": text}], max_tokens=2000)


@router.post("/from-image")
async def from_image(file: UploadFile = File(...), servings: int = Form(2),
                     dietary: str = Form(""), skill: str = Form("beginner")):
    """Photo of ingredients (fridge, counter) in, recipe out."""
    if not (file.content_type or "").startswith("image/"):
        raise HTTPException(400, "Upload an image file")
    data = prepare_image(await file.read())
    text = (f"Identify the ingredients visible in the photo (put them in detected_ingredients), "
            f"then give the best recipe using them. Servings: {servings}. "
            f"Dietary: {dietary or 'none'}. Skill level: {skill}.")
    return ask_json(SYSTEM, [image_block(data), {"type": "text", "text": text}], max_tokens=2000)
