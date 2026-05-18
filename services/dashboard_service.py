"""Dashboard summary — aggregated farm stats."""

from datetime import date, timedelta
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

    avg_weight_raw = db.query(func.avg(Pig.weight_kg)).filter(
        Pig.is_active == True, Pig.weight_kg.isnot(None)
    ).scalar()
    avg_weight = round(float(avg_weight_raw), 1) if avg_weight_raw else None

    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    piglets_this_week = (
        db.query(func.coalesce(func.sum(Farrowing.live_born), 0))
        .filter(
            Farrowing.farrowing_date >= week_start,
            Farrowing.farrowing_date <= today,
        )
        .scalar() or 0
    )

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
        "avg_weight": avg_weight,
        "piglets_this_week": int(piglets_this_week),
        "pen_utilisation": pen_util,
        "health_distribution": {k.value: v for k, v in health_dist.items()},
    }


def get_recent_pigs(db: Session, limit: int = 6) -> list[dict]:
    pigs = (
        db.query(Pig)
        .filter(Pig.is_active == True)
        .order_by(Pig.id.desc())
        .limit(limit)
        .all()
    )
    result = []
    for pig in pigs:
        latest = (
            db.query(HealthRecord)
            .filter(HealthRecord.pig_id == pig.id)
            .order_by(HealthRecord.id.desc())
            .first()
        )
        result.append({
            "ear_tag": pig.ear_tag,
            "pen": pig.pen.name if pig.pen else "—",
            "weight_kg": pig.weight_kg,
            "health_status": latest.status.value if latest else "healthy",
        })
    return result


def get_weekly_piglets(db: Session) -> list[dict]:
    today = date.today()
    weeks = []
    for i in range(6, -1, -1):
        week_end = today - timedelta(weeks=i)
        week_start = week_end - timedelta(days=6)
        count = (
            db.query(func.coalesce(func.sum(Farrowing.live_born), 0))
            .filter(
                Farrowing.farrowing_date >= week_start,
                Farrowing.farrowing_date <= week_end,
            )
            .scalar() or 0
        )
        weeks.append({"week": f"W{7 - i}", "piglets": int(count)})
    return weeks


def get_recent_activity(db: Session, limit: int = 5) -> list[dict]:
    records = (
        db.query(HealthRecord)
        .join(Pig)
        .order_by(HealthRecord.id.desc())
        .limit(limit)
        .all()
    )
    items = []
    for r in records:
        status = r.status.value
        pen_info = f" — pen {r.pig.pen.name}" if r.pig and r.pig.pen else ""
        if status in ("sick", "quarantined"):
            dot = "red"
            text = f"<strong>{r.pig.ear_tag}</strong> — {r.diagnosis or status}{pen_info}"
        elif status == "treated":
            dot = "amber"
            text = f"<strong>{r.pig.ear_tag}</strong> treatment recorded{pen_info}"
        else:
            dot = "green"
            text = f"<strong>{r.pig.ear_tag}</strong> — {r.diagnosis or 'health check'}{pen_info}"
        items.append({
            "dot": dot,
            "text": text,
            "date": r.record_date.isoformat() if r.record_date else "",
        })
    return items
