"""Service layer for Farrowing operations."""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from database.models import Farrowing, Pig
from database.enums import PigCategory
from schemas.farrowing import FarrowingCreate, FarrowingUpdate


def get_farrowing(db: Session, farrowing_id: int) -> Optional[Farrowing]:
    return db.query(Farrowing).filter(Farrowing.id == farrowing_id).first()


def list_farrowings(db: Session, sow_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> list[Farrowing]:
    q = db.query(Farrowing)
    if sow_id:
        q = q.filter(Farrowing.sow_id == sow_id)
    return q.order_by(Farrowing.farrowing_date.desc()).offset(skip).limit(limit).all()


def create_farrowing(db: Session, data: FarrowingCreate) -> Farrowing:
    # Validate sow exists and is a sow/gilt
    sow = db.query(Pig).filter(Pig.id == data.sow_id).first()
    if not sow:
        raise ValueError(f"Pig id={data.sow_id} not found.")
    if sow.category not in (PigCategory.SOW, PigCategory.GILT):
        raise ValueError(f"Pig {sow.ear_tag} is a {sow.category.value}, not a sow/gilt.")
    far = Farrowing(**data.model_dump())
    db.add(far)
    db.commit()
    db.refresh(far)
    return far


def update_farrowing(db: Session, farrowing_id: int, data: FarrowingUpdate) -> Optional[Farrowing]:
    far = get_farrowing(db, farrowing_id)
    if not far:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(far, field, value)
    db.commit()
    db.refresh(far)
    return far


def avg_live_born(db: Session) -> float:
    result = db.query(func.avg(Farrowing.live_born)).scalar()
    return round(result, 1) if result else 0.0
