"""Tesseract OCR wrapper for ear-tag image scanning."""

from pathlib import Path
from typing import Optional, Union

try:
    import pytesseract
    from PIL import Image, ImageFilter
    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False

from config import get_settings


def ocr_image(image_path: Union[str, Path]) -> Optional[str]:
    """Run OCR on an ear-tag image and return raw text.

    Returns None if Tesseract is not installed or image is unreadable.
    """
    if not HAS_TESSERACT:
        return None

    settings = get_settings()
    pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

    try:
        img = Image.open(image_path)
        # Pre-process: convert to grayscale, sharpen
        img = img.convert("L").filter(ImageFilter.SHARPEN)
        text = pytesseract.image_to_string(img, config="--psm 7")  # single line
        return text.strip()
    except Exception as e:
        print(f"OCR error: {e}")
        return None
