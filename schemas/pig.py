"""Pydantic schemas for Pig CRUD."""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field

from database.enums import PigCategory


class PigBase(BaseModel):
    ear_tag: str = Field(..., max_length=30)
    category: PigCategory
    breed: Optional[str] = None
    date_of_birth: Optional[date] = None
    weight_kg: Optional[float] = Field(None, ge=0)
    pen_id: Optional[int] = None
    notes: Optional[str] = None


class PigCreate(PigBase):
    pass


class PigUpdate(BaseModel):
    category: Optional[PigCategory] = None
    breed: Optional[str] = None
    date_of_birth: Optional[date] = None
    weight_kg: Optional[float] = Field(None, ge=0)
    pen_id: Optional[int] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class PigRead(PigBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
