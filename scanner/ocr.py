"""OCR for ear-tag images.

Primary:  Google Cloud Vision API (accurate, handles any font/angle)
Fallback: Tesseract (free, but unreliable for bold marker fonts)
"""

import base64
from pathlib import Path
from typing import Optional, Union

import requests as _requests

try:
    import numpy as np
    import pytesseract
    from PIL import Image, ImageFilter, ImageEnhance, ImageOps
    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False

from config import get_settings


# ── Google Cloud Vision ────────────────────────────────────────────────────

def _ocr_google_vision(image_path: Union[str, Path], api_key: str) -> Optional[str]:
    """Call Google Cloud Vision TEXT_DETECTION and return the full text block."""
    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode("utf-8")

    try:
        resp = _requests.post(
            f"https://vision.googleapis.com/v1/images:annotate?key={api_key}",
            json={
                "requests": [{
                    "image": {"content": image_b64},
                    "features": [{"type": "TEXT_DETECTION"}],
                }]
            },
            timeout=15,
        )
    except _requests.RequestException as e:
        print(f"Vision API request failed: {e}")
        return None

    if resp.status_code != 200:
        print(f"Vision API error {resp.status_code}: {resp.text[:200]}")
        return None

    data = resp.json()
    annotations = data.get("responses", [{}])[0].get("textAnnotations", [])
    if annotations:
        return annotations[0]["description"].strip()
    return None


# ── Tesseract fallback ─────────────────────────────────────────────────────

def _crop_yellow_tag(img: "Image.Image") -> Optional["Image.Image"]:
    """Crop tightly to the yellow ear tag region, or return None."""
    arr = np.array(img.convert("RGB")).astype(int)
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    yellow = (r > 140) & (g > 130) & (b < 110) & ((r - b) > 60) & ((g - b) > 50)
    if yellow.sum() < 300:
        return None
    rows = np.where(np.any(yellow, axis=1))[0]
    cols = np.where(np.any(yellow, axis=0))[0]
    if not len(rows) or not len(cols):
        return None
    pad = 15
    y1, y2 = max(0, int(rows[0]) - pad), min(img.height, int(rows[-1]) + pad)
    x1, x2 = max(0, int(cols[0]) - pad), min(img.width,  int(cols[-1]) + pad)
    cropped = img.crop((x1, y1, x2, y2))
    min_dim = min(cropped.width, cropped.height)
    if min_dim < 300:
        scale = 300 / min_dim
        cropped = cropped.resize(
            (int(cropped.width * scale), int(cropped.height * scale)), Image.LANCZOS
        )
    return cropped


def _ocr_tesseract(image_path: Union[str, Path]) -> Optional[str]:
    """Tesseract fallback — tries 5 passes (4 rotations + inverted)."""
    settings = get_settings()
    pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

    img = Image.open(image_path)
    max_dim = max(img.width, img.height)
    if max_dim > 1200:
        scale = 1200 / max_dim
        img = img.resize((int(img.width * scale), int(img.height * scale)), Image.LANCZOS)

    work = _crop_yellow_tag(img) or img

    def preprocess(i):
        i = i.convert("L")
        i = ImageOps.autocontrast(i, cutoff=2)
        i = ImageEnhance.Contrast(i).enhance(3.0)
        i = i.filter(ImageFilter.SHARPEN).filter(ImageFilter.SHARPEN)
        return i

    base = preprocess(work)
    variants = [
        base,
        base.rotate(90, expand=True),
        base.rotate(180, expand=True),
        base.rotate(270, expand=True),
        ImageOps.invert(base),
    ]
    config = "--psm 11 --oem 1"
    collected, seen = [], set()
    for v in variants:
        text = pytesseract.image_to_string(v, config=config).strip()
        if text and text not in seen:
            seen.add(text)
            collected.append(text)
    return "\n".join(collected) if collected else None


# ── Public entry point ─────────────────────────────────────────────────────

def ocr_image(image_path: Union[str, Path]) -> Optional[str]:
    """Extract text from an ear-tag photo.

    Uses Google Cloud Vision if GOOGLE_VISION_API_KEY is configured,
    otherwise falls back to Tesseract.
    Returns None if nothing is available or nothing is detected.
    """
    settings = get_settings()
    api_key = getattr(settings, "GOOGLE_VISION_API_KEY", None)

    if api_key:
        result = _ocr_google_vision(image_path, api_key)
        if result:
            return result

    if HAS_TESSERACT:
        return _ocr_tesseract(image_path)

    return None
