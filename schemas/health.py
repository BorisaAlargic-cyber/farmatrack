"""Pydantic schemas for HealthRecord CRUD."""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel

from database.enums import HealthStatus


class HealthRecordBase(BaseModel):
    pig_id: int
    status: HealthStatus = HealthStatus.HEALTHY
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None
    vet_name: Optional[str] = None
    record_date: date = date.today()
    next_checkup: Optional[date] = None
    notes: Optional[str] = None


class HealthRecordCreate(HealthRecordBase):
    pass


class HealthRecordUpdate(BaseModel):
    status: Optional[HealthStatus] = None
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None
    vet_name: Optional[str] = None
    next_checkup: Optional[date] = None
    notes: Optional[str] = None


class HealthRecordRead(HealthRecordBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
