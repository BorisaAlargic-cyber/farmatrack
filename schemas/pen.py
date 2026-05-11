"""Pydantic schemas for Pen CRUD."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class PenBase(BaseModel):
    name: str = Field(..., max_length=50)
    capacity: int = Field(..., ge=1)
    pen_type: Optional[str] = None


class PenCreate(PenBase):
    pass


class PenUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=50)
    capacity: Optional[int] = Field(None, ge=1)
    pen_type: Optional[str] = None


class PenRead(PenBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class PenOccupancy(PenRead):
    """Pen with live pig count."""
    current_count: int = 0
