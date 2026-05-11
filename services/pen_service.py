"""Service layer for Pen operations."""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from database.models import Pen, Pig
from schemas.pen import PenCreate, PenUpdate


def get_pen(db: Session, pen_id: int) -> Optional[Pen]:
    return db.query(Pen).filter(Pen.id == pen_id).first()


def list_pens(db: Session, skip: int = 0, limit: int = 50) -> list[Pen]:
    return db.query(Pen).offset(skip).limit(limit).all()


def get_occupancy(db: Session, pen_id: int) -> int:
    return (
        db.query(func.count(Pig.id))
        .filter(Pig.pen_id == pen_id, Pig.is_active == True)
        .scalar() or 0
    )


def create_pen(db: Session, data: PenCreate) -> Pen:
    exists = db.query(Pen).filter(Pen.name == data.name).first()
    if exists:
        raise ValueError(f"Pen '{data.name}' already exists.")
    pen = Pen(**data.model_dump())
    db.add(pen)
    db.commit()
    db.refresh(pen)
    return pen


def update_pen(db: Session, pen_id: int, data: PenUpdate) -> Optional[Pen]:
    pen = get_pen(db, pen_id)
    if not pen:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(pen, field, value)
    db.commit()
    db.refresh(pen)
    return pen
