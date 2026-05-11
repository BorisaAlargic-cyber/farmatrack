"""Dashboard summary — aggregated farm stats."""

from sqlalchemy.orm import Session
from sqlalchemy import func

from database.models import Pig, HealthRecord, Farrowing, Pen
from database.enums import HealthStatus
from services.pig_service import count_by_category
from services.farrowing_service import avg_live_born


def get_summary(db: Session) -> dict:
    total_active = db.query(func.count(Pig.id)).filter(Pig.is_active == True).scalar() or 0
    by_category = count_by_category(db)
    sick_count = (
        db.query(func.count(HealthRecord.id))
        .filter(HealthRecord.status.in_([HealthStatus.SICK, HealthStatus.QUARANTINED]))
        .scalar() or 0
    )
    total_farrowings = db.query(func.count(Farrowing.id)).scalar() or 0
    avg_born = avg_live_born(db)

    pens = db.query(Pen).all()
    pen_util = []
    for p in pens:
        cnt = db.query(func.count(Pig.id)).filter(Pig.pen_id == p.id, Pig.is_active == True).scalar() or 0
        pen_util.append({
            "pen_id": p.id,
            "name": p.name,
            "capacity": p.capacity,
            "current": cnt,
            "utilisation_pct": round(cnt / p.capacity * 100, 1) if p.capacity else 0,
        })

    health_dist = dict(
        db.query(HealthRecord.status, func.count(HealthRecord.id))
        .group_by(HealthRecord.status)
        .all()
    )

    return {
        "total_active_pigs": total_active,
        "by_category": by_category,
        "sick_or_quarantined": sick_count,
        "total_farrowings": total_farrowings,
        "avg_live_born": avg_born,
        "pen_utilisation": pen_util,
        "health_distribution": {k.value: v for k, v in health_dist.items()},
    }
