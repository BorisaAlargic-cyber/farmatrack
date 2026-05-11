"""Service layer for scanning / OCR operations."""

import re
from typing import Optional
from sqlalchemy.orm import Session

from database.models import ScanLog, Pig
from database.enums import ScanSource
from schemas.scan import ScanRequest, ScanResult


# Custom tag format used in the app: 2-4 letters, dash, 3+ digits (SOW-001, FIN-042)
_CUSTOM_TAG = re.compile(r"[A-Z]{2,4}-\d{3,}")

# Real livestock ear tags: 4-12 digit numbers (government-issued IDs)
_NUMERIC_TAG = re.compile(r"\d{4,12}")

# Alphanumeric codes like "OL410", "RS12345" (country/farm prefix + numbers)
_ALPHA_NUM_TAG = re.compile(r"[A-Z]{1,3}\d{3,}")


def _fix_ocr(text: str) -> str:
    """Common OCR corrections: O→0, I→1 in numeric context."""
    return re.sub(r"(?<=\d)[OI]|[OI](?=\d)", lambda m: "0" if m.group() == "O" else "1", text)


def parse_tag(raw: str) -> tuple[Optional[str], float]:
    """Extract an ear-tag from raw OCR text. Returns (tag, confidence).

    Tries four passes in priority order:
      1. Custom app format (SOW-001)  — high confidence
      2. OCR-corrected custom format  — slightly lower
      3. Government numeric ID (4-12 digits) — medium confidence
      4. Alphanumeric code (OL410, RS123) — lower confidence
    Picks the longest match when multiple candidates exist.
    """
    # Normalise: uppercase, strip whitespace/newlines between passes
    lines = [re.sub(r"[^A-Z0-9\-]", "", line.strip().upper()) for line in raw.splitlines()]
    all_text = "".join(lines)

    # Pass 1 — custom format on cleaned text
    matches = _CUSTOM_TAG.findall(all_text)
    if matches:
        return max(matches, key=len), 0.90

    # Pass 2 — custom format after OCR digit corrections
    corrected = _fix_ocr(all_text)
    corrected = re.sub(r"(?<=-)[A-Z0-9]+", lambda m: m.group().replace("O", "0").replace("I", "1"), corrected)
    matches = _CUSTOM_TAG.findall(corrected)
    if matches:
        return max(matches, key=len), 0.85

    # Pass 3 — numeric-only government tag (longest wins)
    # Search each line separately to avoid joining unrelated numbers
    numeric_candidates: list[str] = []
    for line in lines:
        numeric_candidates.extend(_NUMERIC_TAG.findall(line))
    if numeric_candidates:
        best = max(numeric_candidates, key=len)
        return best, 0.75

    # Pass 4 — alphanumeric code like OL410
    alpha_candidates: list[str] = []
    for line in lines:
        alpha_candidates.extend(_ALPHA_NUM_TAG.findall(line))
    if alpha_candidates:
        best = max(alpha_candidates, key=len)
        return best, 0.65

    # Nothing found — return whatever non-empty cleaned text we have
    fallback = all_text if all_text else None
    return fallback, 0.30


def process_scan(db: Session, req: ScanRequest) -> ScanResult:
    parsed_tag, confidence = parse_tag(req.raw_text)

    pig: Optional[Pig] = None
    if parsed_tag:
        pig = db.query(Pig).filter(Pig.ear_tag == parsed_tag).first()

    log = ScanLog(
        pig_id=pig.id if pig else None,
        raw_text=req.raw_text,
        parsed_tag=parsed_tag,
        source=req.source,
        confidence=confidence,
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    if pig:
        return ScanResult(
            parsed_tag=parsed_tag,
            confidence=confidence,
            pig_id=pig.id,
            ear_tag=pig.ear_tag,
            message=f"Matched pig: {pig.ear_tag} ({pig.category.value})",
            raw_text=req.raw_text,
        )
    return ScanResult(
        parsed_tag=parsed_tag,
        confidence=confidence,
        message="No matching pig found." if parsed_tag else "Could not parse tag from scan.",
        raw_text=req.raw_text,
    )


def list_scans(db: Session, skip: int = 0, limit: int = 50) -> list[ScanLog]:
    return db.query(ScanLog).order_by(ScanLog.scanned_at.desc()).offset(skip).limit(limit).all()
