"""Service layer for scanning / OCR operations."""

import re
from typing import Optional
from sqlalchemy.orm import Session

from database.models import ScanLog, Pig
from database.enums import ScanSource
from schemas.scan import ScanRequest, ScanResult


# Pattern: 2-4 uppercase letters, dash, 3+ digits (e.g. SOW-001, FIN-012)
TAG_PATTERN = re.compile(r"[A-Z]{2,4}-\d{3,}")


def _fix_ocr_digits(numeric_part: str) -> str:
    """Apply common OCR corrections only to the numeric portion of a tag."""
    return numeric_part.replace("O", "0").replace("I", "1").replace("l", "1")


def parse_tag(raw: str) -> tuple[Optional[str], float]:
    """Extract ear-tag from raw OCR text. Returns (tag, confidence).

    Two-pass approach:
      1. Clean input and try strict regex match.
      2. If no match, apply OCR digit corrections (O→0, I→1) to the part
         after each dash and retry — this handles cases like "FIN-O12"
         without corrupting letter prefixes like SOW or GLT.
    """
    cleaned = raw.strip().upper().replace(" ", "")
    cleaned = re.sub(r"[^A-Z0-9\-]", "", cleaned)

    # Pass 1: strict match on cleaned input
    match = TAG_PATTERN.search(cleaned)
    if match:
        return match.group(), 0.90

    # Pass 2: fix OCR errors in the numeric portion and retry
    corrected = re.sub(
        r"(?<=-)[A-Z0-9]+",
        lambda m: _fix_ocr_digits(m.group()),
        cleaned,
    )
    match = TAG_PATTERN.search(corrected)
    if match:
        return match.group(), 0.85  # slightly lower confidence for OCR-corrected

    # Fallback
    fallback = cleaned if cleaned else None
    return fallback, 0.40


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
        )
    return ScanResult(
        parsed_tag=parsed_tag,
        confidence=confidence,
        message="No matching pig found." if parsed_tag else "Could not parse tag from scan.",
    )


def list_scans(db: Session, skip: int = 0, limit: int = 50) -> list[ScanLog]:
    return db.query(ScanLog).order_by(ScanLog.scanned_at.desc()).offset(skip).limit(limit).all()
