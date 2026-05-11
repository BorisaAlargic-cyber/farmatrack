"""Service layer for HealthRecord operations."""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from database.models import HealthRecord, Pig
from database.enums import HealthStatus
from schemas.health import HealthRecordCreate, HealthRecordUpdate


def get_health_record(db: Session, record_id: int) -> Optional[HealthRecord]:
    return db.query(HealthRecord).filter(HealthRecord.id == record_id).first()


def list_health_records(
    db: Session,
    *,
    pig_id: Optional[int] = None,
    status: Optional[HealthStatus] = None,
    skip: int = 0,
    limit: int = 100,
) -> list[HealthRecord]:
    q = db.query(HealthRecord)
    if pig_id is not None:
        q = q.filter(HealthRecord.pig_id == pig_id)
    if status is not None:
        q = q.filter(HealthRecord.status == status)
    return q.order_by(HealthRecord.record_date.desc()).offset(skip).limit(limit).all()


def create_health_record(db: Session, data: HealthRecordCreate) -> HealthRecord:
    pig = db.query(Pig).filter(Pig.id == data.pig_id).first()
    if not pig:
        raise ValueError(f"Pig id={data.pig_id} not found.")
    rec = HealthRecord(**data.model_dump())
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


def update_health_record(
    db: Session, record_id: int, data: HealthRecordUpdate
) -> Optional[HealthRecord]:
    rec = get_health_record(db, record_id)
    if not rec:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(rec, field, value)
    db.commit()
    db.refresh(rec)
    return rec


def delete_health_record(db: Session, record_id: int) -> bool:
    rec = get_health_record(db, record_id)
    if not rec:
        return False
    db.delete(rec)
    db.commit()
    return True


def count_by_status(db: Session) -> dict[str, int]:
    rows = (
        db.query(HealthRecord.status, func.count(HealthRecord.id))
        .group_by(HealthRecord.status)
        .all()
    )
    return {status.value: cnt for status, cnt in rows}
