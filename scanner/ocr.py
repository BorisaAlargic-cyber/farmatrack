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

# Only look for characters that appear on ear tags
_WHITELIST = "-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789- --oem 3"

# PSM modes to try, in order of best-fit for a complex photo:
#   11 = sparse text (finds text anywhere in a noisy background — best for photos)
#    6 = single uniform block
#    7 = single text line
#    3 = fully automatic
_PSM_MODES = [11, 6, 7, 3]


def _preprocess(img: "Image.Image") -> "Image.Image":
    """Convert to high-contrast grayscale suitable for Tesseract."""
    img = img.convert("L")
    img = ImageEnhance.Contrast(img).enhance(2.5)
    img = ImageOps.autocontrast(img)
    img = img.filter(ImageFilter.SHARPEN)
    img = img.filter(ImageFilter.SHARPEN)
    return img


def ocr_image(image_path: Union[str, Path]) -> Optional[str]:
    """Run OCR on an ear-tag image and return raw text.

    Tries multiple Tesseract PSM modes on both the normal and inverted image
    so it works on dark-on-light AND light-on-dark ear tags.
    Returns None if Tesseract is not installed or nothing is extracted.
    """
    if not HAS_TESSERACT:
        return None

    settings = get_settings()
    pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

    try:
        img = Image.open(image_path)

        # Downscale very large photos to 1500px on the long side — keeps tag
        # large enough for Tesseract while removing megapixel overhead.
        max_dim = max(img.width, img.height)
        if max_dim > 1500:
            scale = 1500 / max_dim
            img = img.resize(
                (int(img.width * scale), int(img.height * scale)),
                Image.LANCZOS,
            )

        processed = _preprocess(img)
        inverted = ImageOps.invert(processed)

        collected: list[str] = []
        for variant in (processed, inverted):
            for psm in _PSM_MODES:
                text = pytesseract.image_to_string(
                    variant, config=f"--psm {psm} {_WHITELIST}"
                ).strip()
                if text:
                    collected.append(text)

        return "\n".join(collected) if collected else None

    except Exception as e:
        print(f"OCR error: {e}")
        return None
