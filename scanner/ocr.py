"""Tesseract OCR wrapper for ear-tag image scanning."""

from pathlib import Path
from typing import Optional, Union

try:
    import numpy as np
    import pytesseract
    from PIL import Image, ImageFilter, ImageEnhance, ImageOps
    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False

from config import get_settings

# PSM 6 = uniform block of text (best for a cropped tag image)
# PSM 7 = single text line (picks up the large animal-ID number)
_CONFIGS = ["--psm 6 --oem 1", "--psm 7 --oem 1"]
_ROTATIONS = [0, 90, 180, 270]


def _crop_yellow_tag(img: "Image.Image") -> Optional["Image.Image"]:
    """Detect the yellow ear tag and return a tightly-cropped, upscaled crop.

    Yellow pig tags: high R, high G, low B.
    Returns None if no significant yellow region is found.
    """
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
    y1 = max(0, int(rows[0]) - pad)
    y2 = min(img.height, int(rows[-1]) + pad)
    x1 = max(0, int(cols[0]) - pad)
    x2 = min(img.width, int(cols[-1]) + pad)

    cropped = img.crop((x1, y1, x2, y2))

    # Upscale small crops so Tesseract has enough resolution
    min_dim = min(cropped.width, cropped.height)
    if min_dim < 300:
        scale = 300 / min_dim
        cropped = cropped.resize(
            (int(cropped.width * scale), int(cropped.height * scale)),
            Image.LANCZOS,
        )

    return cropped


def _preprocess(img: "Image.Image") -> "Image.Image":
    """High-contrast grayscale — dark ink on yellow becomes black on white."""
    img = img.convert("L")
    img = ImageOps.autocontrast(img, cutoff=2)
    img = ImageEnhance.Contrast(img).enhance(3.0)
    img = img.filter(ImageFilter.SHARPEN)
    img = img.filter(ImageFilter.SHARPEN)
    return img


def ocr_image(image_path: Union[str, Path]) -> Optional[str]:
    """Run OCR on an ear-tag image and return raw text.

    Strategy:
      1. Detect and crop to the yellow tag region (removes pig-skin noise).
      2. Try all 4 rotations — tags are often upside-down in photos.
      3. Two PSM modes per rotation (block + single-line).
    Returns None if Tesseract is not installed or nothing is extracted.
    """
    if not HAS_TESSERACT:
        return None

    settings = get_settings()
    pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

    try:
        img = Image.open(image_path)

        # Resize large photos — 1200px is enough, speeds up yellow detection
        max_dim = max(img.width, img.height)
        if max_dim > 1200:
            scale = 1200 / max_dim
            img = img.resize(
                (int(img.width * scale), int(img.height * scale)),
                Image.LANCZOS,
            )

        # Prefer cropped tag; fall back to full image
        work = _crop_yellow_tag(img) or img

        collected: list[str] = []
        seen: set[str] = set()

        for angle in _ROTATIONS:
            rotated = work.rotate(angle, expand=True)
            processed = _preprocess(rotated)

            for cfg in _CONFIGS:
                text = pytesseract.image_to_string(processed, config=cfg).strip()
                if text and text not in seen:
                    seen.add(text)
                    collected.append(text)

        return "\n".join(collected) if collected else None

    except Exception as e:
        print(f"OCR error: {e}")
        return None
