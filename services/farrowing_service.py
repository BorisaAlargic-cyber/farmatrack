"""Service layer for Farrowing operations."""

from datetime import date
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
    return q.order_by(Farrowing.created_at.asc()).offset(skip).limit(limit).all()


def list_farrowings_for_card(db: Session, sow_id: int) -> list[dict]:
    """Return enriched farrowing dicts with farrowing_number and expected_farrowing_date."""
    farrowings = list_farrowings(db, sow_id=sow_id)
    result = []
    for i, f in enumerate(farrowings):
        result.append({
            "id": f.id,
            "sow_id": f.sow_id,
            "farrowing_number": i + 1,
            "insemination_date": f.insemination_date,
            "expected_farrowing_date": f.expected_farrowing_date,
            "farrowing_date": f.farrowing_date,
            "live_born": f.live_born,
            "stillborn": f.stillborn,
            "mummified": f.mummified,
            "weaned_count": f.weaned_count,
            "wean_date": f.wean_date,
            "notes": f.notes,
            "total_born": f.total_born,
            "created_at": f.created_at,
        })
    return result


def create_farrowing(db: Session, data: FarrowingCreate) -> Farrowing:
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


def add_insemination(db: Session, sow_id: int, insemination_date: date) -> Farrowing:
    """Create a new reproductive cycle record starting with insemination."""
    data = FarrowingCreate(sow_id=sow_id, insemination_date=insemination_date)
    return create_farrowing(db, data)


def record_farrowing(
    db: Session,
    farrowing_id: int,
    farrowing_date: date,
    live_born: int,
    stillborn: int,
    mummified: int,
) -> Optional[Farrowing]:
    """Record the actual farrowing outcome on an existing insemination record."""
    data = FarrowingUpdate(
        farrowing_date=farrowing_date,
        live_born=live_born,
        stillborn=stillborn,
        mummified=mummified,
    )
    return update_farrowing(db, farrowing_id, data)


def update_farrowing(db: Session, farrowing_id: int, data: FarrowingUpdate) -> Optional[Farrowing]:
    far = get_farrowing(db, farrowing_id)
    if not far:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(far, field, value)
    db.commit()
    db.refresh(far)
    return far


def list_upcoming_farrowings(db: Session, days_ahead: int) -> list[dict]:
    """Return pending farrowings (inseminated, not yet farrowed) up to days_ahead from today."""
    from datetime import timedelta
    today = date.today()
    cutoff = today + timedelta(days=days_ahead)

    pending = db.query(Farrowing).filter(
        Farrowing.insemination_date.isnot(None),
        Farrowing.farrowing_date.is_(None),
    ).all()

    result = []
    for f in pending:
        exp = f.expected_farrowing_date
        if exp is None:
            continue
        if days_ahead == 0:
            if exp != today:
                continue
        elif days_ahead == 1:
            tomorrow = today + timedelta(days=1)
            if exp != tomorrow:
                continue
        else:
            if exp > cutoff:
                continue

        days_left = (exp - today).days
        sow = f.sow
        result.append({
            "farrowing_id": f.id,
            "sow_id": f.sow_id,
            "ear_tag": sow.ear_tag if sow else "—",
            "pen": sow.pen.name if (sow and sow.pen) else "—",
            "insemination_date": f.insemination_date,
            "expected_farrowing_date": exp,
            "days_left": days_left,
        })

    result.sort(key=lambda r: r["expected_farrowing_date"])
    return result


def avg_live_born(db: Session) -> float:
    result = db.query(func.avg(Farrowing.live_born)).scalar()
    return round(result, 1) if result else 0.0
