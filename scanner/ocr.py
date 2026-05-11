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

# Characters that appear on ear tags (no lowercase, no punctuation)
_WHITELIST = "-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789- --oem 3"

# PSM 11 (sparse text) is best for finding a small tag in a complex photo.
# PSM 6 (block) and PSM 3 (auto) are fallbacks.
_PSM_MODES = [11, 6, 3]

# Pig tags can be at any angle — try all four cardinal rotations.
_ROTATIONS = [0, 90, 180, 270]


def _preprocess(img: "Image.Image") -> "Image.Image":
    """High-contrast grayscale optimised for yellow plastic tags with dark ink."""
    img = img.convert("L")
    # Stretch contrast so dark ink on yellow background becomes near-black on white
    img = ImageOps.autocontrast(img, cutoff=2)
    img = ImageEnhance.Contrast(img).enhance(3.0)
    img = img.filter(ImageFilter.SHARPEN)
    img = img.filter(ImageFilter.SHARPEN)
    return img


def ocr_image(image_path: Union[str, Path]) -> Optional[str]:
    """Run OCR on an ear-tag image and return raw text.

    Tries every combination of 4 rotations × 3 PSM modes × normal/inverted
    so a tag photographed upside-down or sideways is still recognised.
    Returns None if Tesseract is not installed or nothing is extracted.
    """
    if not HAS_TESSERACT:
        return None

    settings = get_settings()
    pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

    try:
        img = Image.open(image_path)

        # Resize so the long side is ≤1200px — large enough for Tesseract,
        # small enough to process quickly.
        max_dim = max(img.width, img.height)
        if max_dim > 1200:
            scale = 1200 / max_dim
            img = img.resize(
                (int(img.width * scale), int(img.height * scale)),
                Image.LANCZOS,
            )

        collected: list[str] = []
        seen: set[str] = set()

        for angle in _ROTATIONS:
            rotated = img.rotate(angle, expand=True)
            processed = _preprocess(rotated)
            inverted = ImageOps.invert(processed)

            for variant in (processed, inverted):
                for psm in _PSM_MODES:
                    text = pytesseract.image_to_string(
                        variant, config=f"--psm {psm} {_WHITELIST}"
                    ).strip()
                    if text and text not in seen:
                        seen.add(text)
                        collected.append(text)

        return "\n".join(collected) if collected else None

    except Exception as e:
        print(f"OCR error: {e}")
        return None
