"""Audio input: speech to text so users can talk to the kitchen assistant."""
import os
import tempfile

from fastapi import APIRouter, File, HTTPException, UploadFile

router = APIRouter(prefix="/api/audio", tags=["audio"])
MAX_AUDIO_BYTES = 25 * 1024 * 1024
_model = None


def transcribe_bytes(data: bytes, suffix: str = ".webm") -> str:
    global _model
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        raise HTTPException(501, "Audio support not installed. Run: pip install -r requirements-audio.txt") from None
    if _model is None:
        _model = WhisperModel(os.getenv("WHISPER_MODEL", "tiny"), compute_type="int8")
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(data)
        path = tmp.name
    try:
        segments, _ = _model.transcribe(path)
        return " ".join(s.text.strip() for s in segments).strip()
    finally:
        os.unlink(path)


@router.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    if not (file.content_type or "").startswith(("audio/", "video/webm")):
        raise HTTPException(400, "Upload an audio file")
    data = await file.read()
    if len(data) > MAX_AUDIO_BYTES:
        raise HTTPException(413, "Audio too large (max 25 MB)")
    text = transcribe_bytes(data, os.path.splitext(file.filename or "")[1] or ".webm")
    if not text:
        raise HTTPException(422, "No speech detected")
    return {"text": text}
