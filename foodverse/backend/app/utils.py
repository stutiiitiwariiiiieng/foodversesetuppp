"""Input hardening shared by image endpoints (robustness: odd formats, huge photos)."""
import cv2
import numpy as np
from fastapi import HTTPException

MAX_IMAGE_BYTES = 10 * 1024 * 1024


def prepare_image(data: bytes, max_side: int = 1568) -> bytes:
    """Validate, downscale and re-encode any readable image as JPEG."""
    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(413, "Image too large (max 10 MB)")
    img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(400, "Could not read image. Use JPG, PNG or WebP.")
    h, w = img.shape[:2]
    scale = max_side / max(h, w)
    if scale < 1:
        img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 88])
    if not ok:
        raise HTTPException(400, "Could not process image")
    return buf.tobytes()
