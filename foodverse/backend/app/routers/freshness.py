from fastapi import APIRouter, File, HTTPException, UploadFile

from app import features, scoring
from app.llm import ask_json, image_block
from app.utils import prepare_image

router = APIRouter(prefix="/api/freshness", tags=["freshness"])

SYSTEM = """You assess food freshness from a photo using color, texture, discoloration,
mold, wilting, bruising and surface patterns. Account for lighting and natural ripening:
a brown-spotted banana is ripe, not necessarily spoiled. When evidence is ambiguous, lean
cautious. Schema:
{"food": str, "status": "Fresh"|"Moderately Fresh"|"Spoiled",
 "freshness_score": integer 0-100, "confidence": "low"|"medium"|"high",
 "safe_to_eat": boolean, "indicators": [{"signal": str, "observation": str,
 "severity": "good"|"warning"|"bad"}], "recommendation": str, "storage_tip": str,
 "disclaimer": "Visual estimate only. When in doubt, throw it out."}
If no food is visible return {"error": "No food detected"}."""


@router.post("/check")
async def check(file: UploadFile = File(...)):
    if not (file.content_type or "").startswith("image/"):
        raise HTTPException(400, "Upload an image file")
    data = prepare_image(await file.read())
    img = features.decode(data)
    feats = features.extract(img)
    hint = features.describe(feats)
    out = ask_json(SYSTEM, [image_block(data), {"type": "text", "text": "Assess freshness.\n" + hint}])
    if "error" in out:
        raise HTTPException(422, out["error"])
    out = scoring.finalize_freshness(out, feats)
    out["features"] = feats
    out["quality_warnings"] = features.quality_warnings(img)
    return out
