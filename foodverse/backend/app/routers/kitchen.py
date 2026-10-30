"""Smart Kitchen Assistant: contextual, turn-by-turn cooking help, optionally from a photo."""
import json

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.llm import ask_json, image_block
from app.utils import prepare_image

router = APIRouter(prefix="/api/kitchen", tags=["kitchen"])

SYSTEM = """You are a live kitchen assistant helping someone cook right now. Use the recipe
context, the conversation so far, and the photo (if given) to judge doneness, texture,
color, seasoning and mistakes. Be brief and concrete: they are standing at the stove.
Flag real safety issues (raw meat handling, oil fires, burns, undercooked poultry).
Schema:
{"reply": str, "next_action": str, "timer_minutes": number|null,
 "safety_flag": boolean, "safety_note": str}"""


@router.post("/assist")
async def assist(
    message: str = Form(...),
    history: str = Form("[]"),
    recipe_context: str = Form(""),
    file: UploadFile | None = File(None),
):
    if not message.strip():
        raise HTTPException(400, "Message is empty")
    try:
        turns = json.loads(history)
        assert isinstance(turns, list)
    except Exception:
        raise HTTPException(400, "history must be a JSON list") from None
    transcript = "\n".join(f"{t.get('role', 'user')}: {t.get('text', '')}" for t in turns[-10:])
    text = (f"Recipe context: {recipe_context or 'none'}\n"
            f"Conversation so far:\n{transcript or '(start)'}\nUser now says: {message}")
    content = []
    if file is not None:
        if not (file.content_type or "").startswith("image/"):
            raise HTTPException(400, "Attach an image file")
        content.append(image_block(prepare_image(await file.read())))
    content.append({"type": "text", "text": text})
    return ask_json(SYSTEM, content, max_tokens=800)
