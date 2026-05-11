"""OCR for ear-tag images.

Primary:  Google Gemini Vision API (free, just a Google account, very accurate)
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

_GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-1.5-flash:generateContent?key={key}"
)

_PROMPT = (
    "This is a photo of a yellow plastic pig ear tag. "
    "Read the large number printed on it (usually 4-6 digits). "
    "Return ONLY that number — no explanation, no other text."
)


# ── Gemini Vision ──────────────────────────────────────────────────────────

def _ocr_gemini(image_path: Union[str, Path], api_key: str) -> Optional[str]:
    """Call Gemini 1.5 Flash vision and extract the tag number."""
    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode("utf-8")

    # Detect mime type from extension
    ext = Path(image_path).suffix.lower()
    mime = {"jpg": "image/jpeg", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".png": "image/png"}.get(ext, "image/jpeg")

    payload = {
        "contents": [{
            "parts": [
                {"text": _PROMPT},
                {"inline_data": {"mime_type": mime, "data": image_b64}},
            ]
        }]
    }

    try:
        resp = _requests.post(
            _GEMINI_URL.format(key=api_key),
            json=payload,
            timeout=20,
        )
    except _requests.RequestException as e:
        print(f"Gemini API request failed: {e}")
        return None

    if resp.status_code != 200:
        print(f"Gemini API error {resp.status_code}: {resp.text[:200]}")
        return None

    try:
        text = (
            resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        )
        return text if text else None
    except (KeyError, IndexError):
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
    """Tesseract fallback — 5 passes (4 rotations + inverted)."""
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
        return i.filter(ImageFilter.SHARPEN).filter(ImageFilter.SHARPEN)

    base = preprocess(work)
    variants = [
        base,
        base.rotate(90, expand=True),
        base.rotate(180, expand=True),
        base.rotate(270, expand=True),
        ImageOps.invert(base),
    ]
    collected, seen = [], set()
    for v in variants:
        text = pytesseract.image_to_string(v, config="--psm 11 --oem 1").strip()
        if text and text not in seen:
            seen.add(text)
            collected.append(text)
    return "\n".join(collected) if collected else None


# ── Public entry point ─────────────────────────────────────────────────────

def ocr_image(image_path: Union[str, Path]) -> Optional[str]:
    """Extract text from an ear-tag photo.

    Uses Gemini Vision if GOOGLE_VISION_API_KEY is set in settings,
    otherwise falls back to Tesseract.
    """
    settings = get_settings()
    api_key = settings.GOOGLE_VISION_API_KEY

    if api_key:
        result = _ocr_gemini(image_path, api_key)
        if result:
            return result

    if HAS_TESSERACT:
        return _ocr_tesseract(image_path)

    return None
