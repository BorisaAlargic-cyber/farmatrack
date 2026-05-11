"""Service layer for Pig operations."""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from database.models import Pig
from database.enums import PigCategory
from schemas.pig import PigCreate, PigUpdate


def get_pig(db: Session, pig_id: int) -> Optional[Pig]:
    return db.query(Pig).filter(Pig.id == pig_id).first()


def get_pig_by_tag(db: Session, ear_tag: str) -> Optional[Pig]:
    return db.query(Pig).filter(Pig.ear_tag == ear_tag).first()


def list_pigs(
    db: Session,
    *,
    category: Optional[PigCategory] = None,
    pen_id: Optional[int] = None,
    active_only: bool = True,
    skip: int = 0,
    limit: int = 100,
) -> list[Pig]:
    q = db.query(Pig)
    if active_only:
        q = q.filter(Pig.is_active == True)
    if category:
        q = q.filter(Pig.category == category)
    if pen_id is not None:
        q = q.filter(Pig.pen_id == pen_id)
    return q.offset(skip).limit(limit).all()


def count_by_category(db: Session) -> dict[str, int]:
    rows = (
        db.query(Pig.category, func.count(Pig.id))
        .filter(Pig.is_active == True)
        .group_by(Pig.category)
        .all()
    )
    return {cat.value: cnt for cat, cnt in rows}


def create_pig(db: Session, data: PigCreate) -> Pig:
    pig = Pig(**data.model_dump())
    db.add(pig)
    db.commit()
    db.refresh(pig)
    return pig


def update_pig(db: Session, pig_id: int, data: PigUpdate) -> Optional[Pig]:
    pig = get_pig(db, pig_id)
    if not pig:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(pig, field, value)
    db.commit()
    db.refresh(pig)
    return pig


def deactivate_pig(db: Session, pig_id: int) -> Optional[Pig]:
    pig = get_pig(db, pig_id)
    if not pig:
        return None
    pig.is_active = False
    db.commit()
    db.refresh(pig)
    return pig
