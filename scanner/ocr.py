"""Tesseract OCR wrapper for ear-tag image scanning."""

from pathlib import Path
from typing import Optional, Union

try:
    import pytesseract
    from PIL import Image, ImageFilter, ImageEnhance, ImageOps
    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False

from config import get_settings

# PSM 11 = sparse text: finds text anywhere in a complex photo background.
# oem 1 = LSTM only (faster than oem 3, handles rotated/handwritten text well).
# Character whitelist keeps Tesseract focused on tag characters only.
_CONFIG = "--psm 11 --oem 1 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-"


def _preprocess(img: "Image.Image") -> "Image.Image":
    """High-contrast grayscale for yellow plastic tags with dark ink."""
    img = img.convert("L")
    img = ImageOps.autocontrast(img, cutoff=2)
    img = ImageEnhance.Contrast(img).enhance(3.0)
    img = img.filter(ImageFilter.SHARPEN)
    img = img.filter(ImageFilter.SHARPEN)
    return img


def ocr_image(image_path: Union[str, Path]) -> Optional[str]:
    """Run OCR on an ear-tag image and return raw text.

    Tries 5 passes: 4 cardinal rotations + inverted original.
    Returns None if Tesseract is not installed or nothing is extracted.
    """
    if not HAS_TESSERACT:
        return None

    settings = get_settings()
    pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

    try:
        img = Image.open(image_path)

        # Keep long side ≤ 1200 px — enough for Tesseract, fast to process.
        max_dim = max(img.width, img.height)
        if max_dim > 1200:
            scale = 1200 / max_dim
            img = img.resize(
                (int(img.width * scale), int(img.height * scale)),
                Image.LANCZOS,
            )

        base = _preprocess(img)

        # 5 attempts: 0°/90°/180°/270° + colour-inverted original
        # (inverted catches white-on-yellow or white-on-blue tags)
        variants = [
            base,
            base.rotate(90, expand=True),
            base.rotate(180, expand=True),
            base.rotate(270, expand=True),
            ImageOps.invert(base),
        ]

        collected: list[str] = []
        seen: set[str] = set()
        for v in variants:
            text = pytesseract.image_to_string(v, config=_CONFIG).strip()
            if text and text not in seen:
                seen.add(text)
                collected.append(text)

        return "\n".join(collected) if collected else None

    except Exception as e:
        print(f"OCR error: {e}")
        return None
