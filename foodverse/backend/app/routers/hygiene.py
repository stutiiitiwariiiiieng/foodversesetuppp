import tempfile, os
import cv2
from fastapi import APIRouter, File, HTTPException, Query, UploadFile

from app import scoring
from app.llm import ask_json, image_block

router = APIRouter(prefix="/api/hygiene", tags=["hygiene"])
MAX_FRAMES = 8
MAX_VIDEO_BYTES = 200 * 1024 * 1024

SYSTEM = """You audit kitchen hygiene from sampled video frames (in time order).
Check: gloves, hair caps/nets, aprons, handling of food, clean surfaces, cross-contamination,
visible pests or clutter. Only report what is visible; mark unclear items "unknown".
Schema:
{"overall_score": integer 0-100, "risk_level": "low"|"medium"|"high",
 "checks": [{"item": "Gloves"|"Hair cap"|"Apron"|"Food handling"|"Surface cleanliness"|"Cross-contamination",
   "status": "pass"|"fail"|"unknown", "evidence": str}],
 "violations": [{"frame": integer, "description": str}],
 "alerts": [str], "recommendations": [str],
 "disclaimer": "AI-assisted screening; not a substitute for official inspection."}"""


def sample_frames(path: str, n: int = MAX_FRAMES) -> list[bytes]:
    cap = cv2.VideoCapture(path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total <= 0:
        raise HTTPException(400, "Could not read video")
    frames = []
    for i in range(n):
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(total * (i + 0.5) / n))
        ok, frame = cap.read()
        if not ok:
            continue
        h, w = frame.shape[:2]
        scale = 768 / max(h, w)
        if scale < 1:
            frame = cv2.resize(frame, (int(w * scale), int(h * scale)))
        ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        if ok:
            frames.append(buf.tobytes())
    cap.release()
    return frames


@router.post("/analyze")
async def analyze(file: UploadFile = File(...), frames: int = Query(MAX_FRAMES, ge=4, le=16)):
    if not (file.content_type or "").startswith("video/"):
        raise HTTPException(400, "Upload a video file")
    suffix = os.path.splitext(file.filename or "")[1] or ".mp4"
    body = await file.read()
    if len(body) > MAX_VIDEO_BYTES:
        raise HTTPException(413, "Video too large (max 200 MB)")
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(body)
        path = tmp.name
    try:
        sampled = sample_frames(path, frames)
    finally:
        os.unlink(path)
    if not sampled:
        raise HTTPException(400, "No frames could be extracted")
    content = []
    for i, f in enumerate(sampled, 1):
        content += [{"type": "text", "text": f"Frame {i}:"}, image_block(f)]
    content.append({"type": "text", "text": "Audit hygiene across these frames."})
    out = ask_json(SYSTEM, content, max_tokens=2000)
    out["ai_overall_score"] = out.get("overall_score")
    out.update(scoring.hygiene_compliance(out.get("checks", [])))  # rule-based score and risk
    out["alerts"] = list(dict.fromkeys(out.get("alerts", []) + out["rule_alerts"]))
    out["frames_analyzed"] = len(sampled)
    return out
