"""Pydantic schemas for ScanLog."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from database.enums import ScanSource


class ScanRequest(BaseModel):
    """Incoming scan — either raw OCR text or a manual entry."""
    raw_text: str
    source: ScanSource = ScanSource.EAR_TAG


class ScanResult(BaseModel):
    parsed_tag: Optional[str] = None
    confidence: Optional[float] = None
    pig_id: Optional[int] = None
    ear_tag: Optional[str] = None
    message: str


class ScanLogRead(BaseModel):
    id: int
    pig_id: Optional[int]
    raw_text: str
    parsed_tag: Optional[str]
    source: ScanSource
    confidence: Optional[float]
    scanned_at: datetime

    model_config = {"from_attributes": True}
