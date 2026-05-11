"""CRUD router for HealthRecords."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database.connection import get_db
from database.enums import HealthStatus
from schemas.health import HealthRecordCreate, HealthRecordRead, HealthRecordUpdate
from services import health_service

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/", response_model=list[HealthRecordRead])
def list_health_records(
    pig_id: Optional[int] = None,
    status: Optional[HealthStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return health_service.list_health_records(
        db, pig_id=pig_id, status=status, skip=skip, limit=limit,
    )


@router.get("/{record_id}", response_model=HealthRecordRead)
def get_health_record(record_id: int, db: Session = Depends(get_db)):
    rec = health_service.get_health_record(db, record_id)
    if not rec:
        raise HTTPException(404, "Health record not found")
    return rec


@router.post("/", response_model=HealthRecordRead, status_code=201)
def create_health_record(data: HealthRecordCreate, db: Session = Depends(get_db)):
    try:
        return health_service.create_health_record(db, data)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.patch("/{record_id}", response_model=HealthRecordRead)
def update_health_record(record_id: int, data: HealthRecordUpdate, db: Session = Depends(get_db)):
    rec = health_service.update_health_record(db, record_id, data)
    if not rec:
        raise HTTPException(404, "Health record not found")
    return rec


@router.delete("/{record_id}", status_code=204)
def delete_health_record(record_id: int, db: Session = Depends(get_db)):
    deleted = health_service.delete_health_record(db, record_id)
    if not deleted:
        raise HTTPException(404, "Health record not found")
