"""OCR for ear-tag images via OpenRouter vision API."""

import base64
from pathlib import Path
from typing import Optional, Union

import requests as _requests

from config import get_settings

_URL = "https://openrouter.ai/api/v1/chat/completions"
_MODEL = "openai/gpt-4o-mini"

_PROMPT = (
    "Look at this image and read the number on it. "
    "It may be a pig ear tag, a piece of paper, or any object with a number written or printed on it. "
    "Return ONLY the number — no explanation, no other text. "
    "If there are multiple numbers, return the largest or most prominent one."
)


def ocr_image(image_path: Union[str, Path]) -> Optional[str]:
    """Extract a number from an image using OpenRouter vision."""
    settings = get_settings()
    api_key = settings.OPENROUTER_API_KEY
    if not api_key:
        return None

    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode("utf-8")

    ext = Path(image_path).suffix.lower()
    mime = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png"}.get(ext, "image/jpeg")

    payload = {
        "model": _MODEL,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": _PROMPT},
                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{image_b64}"}},
            ],
        }],
    }

    try:
        resp = _requests.post(
            _URL,
            headers={"Authorization": f"Bearer {api_key}"},
            json=payload,
            timeout=30,
        )
    except _requests.RequestException as e:
        print(f"OpenRouter request failed: {e}")
        return None

    if resp.status_code != 200:
        print(f"OpenRouter error {resp.status_code}: {resp.text[:200]}")
        return None

    try:
        text = resp.json()["choices"][0]["message"]["content"].strip()
        return text if text else None
    except (KeyError, IndexError):
        return None
