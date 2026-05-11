"""Pydantic schemas for Farrowing CRUD."""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class FarrowingBase(BaseModel):
    sow_id: int
    farrowing_date: date
    live_born: int = Field(..., ge=0)
    stillborn: int = Field(0, ge=0)
    mummified: int = Field(0, ge=0)
    weaned_count: Optional[int] = Field(None, ge=0)
    wean_date: Optional[date] = None
    notes: Optional[str] = None


class FarrowingCreate(FarrowingBase):
    pass


class FarrowingUpdate(BaseModel):
    live_born: Optional[int] = Field(None, ge=0)
    stillborn: Optional[int] = Field(None, ge=0)
    mummified: Optional[int] = Field(None, ge=0)
    weaned_count: Optional[int] = Field(None, ge=0)
    wean_date: Optional[date] = None
    notes: Optional[str] = None


class FarrowingRead(FarrowingBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
