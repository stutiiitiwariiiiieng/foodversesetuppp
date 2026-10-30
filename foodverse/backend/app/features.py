"""Activity 3.1: image preprocessing and freshness-related feature extraction (OpenCV)."""
import cv2
import numpy as np


def decode(jpeg: bytes):
    return cv2.imdecode(np.frombuffer(jpeg, np.uint8), cv2.IMREAD_COLOR)


def preprocess(img, side: int = 512):
    """Resize, even out lighting (CLAHE on lightness) and denoise."""
    h, w = img.shape[:2]
    s = side / max(h, w)
    if s != 1:
        img = cv2.resize(img, (int(w * s), int(h * s)),
                         interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC)
    l, a, b = cv2.split(cv2.cvtColor(img, cv2.COLOR_BGR2LAB))
    l = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(l)
    img = cv2.cvtColor(cv2.merge((l, a, b)), cv2.COLOR_LAB2BGR)
    return cv2.bilateralFilter(img, 5, 40, 40)


def quality_warnings(img) -> list:
    out = []
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if min(h, w) < 200:
        out.append("Low resolution image. Results may be less reliable.")
    if gray.mean() < 50:
        out.append("Image is very dark. Retake in better light.")
    elif gray.mean() > 235:
        out.append("Image is overexposed. Retake away from direct glare.")
    if cv2.Laplacian(gray, cv2.CV_64F).var() < 20:
        out.append("Image looks blurry. Hold steady and refocus.")
    return out


def extract(img) -> dict:
    p = preprocess(img)
    hsv = cv2.cvtColor(p, cv2.COLOR_BGR2HSV)
    H, S, V = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    gray = cv2.cvtColor(p, cv2.COLOR_BGR2GRAY)
    n = H.size
    frac = lambda m: round(float(m.sum()) / n, 4)  # noqa: E731
    h, w = gray.shape
    c = (slice(h // 5, h - h // 5), slice(w // 5, w - w // 5))
    pale = (S[c] < 40) & (V[c] > 150)
    sat = S > 40
    return {
        "mean_brightness": round(float(V.mean()), 1),
        "mean_saturation": round(float(S.mean()), 1),
        "dark_ratio": frac(V < 60),
        "brown_dark_ratio": frac(((H >= 8) & (H <= 25) & (S > 70) & (V < 150)) | (V < 60)),
        "green_ratio": frac((H >= 35) & (H <= 85) & (S > 50)),
        "yellow_ratio": frac((H > 20) & (H < 35) & (S > 80)),
        "pale_patch_ratio": round(float(pale.mean()), 4),
        "color_variation": round(float(np.std(H[sat])) if sat.any() else 0.0, 1),
        "texture_sharpness": round(float(cv2.Laplacian(gray, cv2.CV_64F).var()), 1),
        "edge_density": round(float((cv2.Canny(gray, 80, 160) > 0).mean()), 4),
    }


def describe(f: dict) -> str:
    return ("Measured image features (supporting evidence only; judge mainly from the photo): "
            f"brown/dark area {f['brown_dark_ratio']:.0%}, green {f['green_ratio']:.0%}, "
            f"yellow {f['yellow_ratio']:.0%}, pale/fuzzy patches in center {f['pale_patch_ratio']:.0%}, "
            f"color variation {f['color_variation']}, texture sharpness {f['texture_sharpness']}, "
            f"brightness {f['mean_brightness']}.")
