"""Pydantic schemas for Farrowing CRUD."""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class FarrowingCreate(BaseModel):
    sow_id: int
    insemination_date: Optional[date] = None
    farrowing_date: Optional[date] = None
    live_born: Optional[int] = Field(None, ge=0)
    stillborn: int = Field(0, ge=0)
    mummified: int = Field(0, ge=0)
    weaned_count: Optional[int] = Field(None, ge=0)
    wean_date: Optional[date] = None
    notes: Optional[str] = None


class FarrowingUpdate(BaseModel):
    insemination_date: Optional[date] = None
    farrowing_date: Optional[date] = None
    live_born: Optional[int] = Field(None, ge=0)
    stillborn: Optional[int] = Field(None, ge=0)
    mummified: Optional[int] = Field(None, ge=0)
    weaned_count: Optional[int] = Field(None, ge=0)
    wean_date: Optional[date] = None
    notes: Optional[str] = None


class FarrowingRead(BaseModel):
    id: int
    sow_id: int
    farrowing_number: int = 0
    insemination_date: Optional[date] = None
    expected_farrowing_date: Optional[date] = None
    farrowing_date: Optional[date] = None
    live_born: Optional[int] = None
    stillborn: int = 0
    mummified: int = 0
    weaned_count: Optional[int] = None
    wean_date: Optional[date] = None
    notes: Optional[str] = None
    total_born: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}
