"""Seed the database with demo data for development / testing."""

from datetime import date, timedelta
import random

from database.connection import SessionLocal, init_db
from database.models import Pen, Pig, HealthRecord, Farrowing, ScanLog
from database.enums import PigCategory, HealthStatus, ScanSource


def seed() -> None:
    init_db()
    db = SessionLocal()

    # Skip if data already exists
    if db.query(Pen).first():
        print("Database already seeded — skipping.")
        db.close()
        return

    # --- Pens ---
    pens_data = [
        ("Farrowing-A", 10, "farrowing"),
        ("Farrowing-B", 10, "farrowing"),
        ("Nursery-1", 30, "nursery"),
        ("Nursery-2", 30, "nursery"),
        ("Finishing-1", 50, "finishing"),
        ("Finishing-2", 50, "finishing"),
        ("Gilt-Dev", 20, "development"),
        ("Quarantine", 10, "quarantine"),
    ]
    pens = []
    for name, cap, ptype in pens_data:
        p = Pen(name=name, capacity=cap, pen_type=ptype)
        db.add(p)
        pens.append(p)
    db.flush()

    breeds = ["Large White", "Landrace", "Duroc", "Pietrain", "Hampshire"]
    today = date.today()

    # --- Sows ---
    sows = []
    for i in range(1, 9):
        sow = Pig(
            ear_tag=f"SOW-{i:03d}",
            category=PigCategory.SOW,
            breed=random.choice(breeds),
            date_of_birth=today - timedelta(days=random.randint(700, 1200)),
            weight_kg=round(random.uniform(180, 260), 1),
            pen_id=pens[0].id if i <= 4 else pens[1].id,
            notes=f"Sow #{i} — AI breeding programme",
        )
        db.add(sow)
        sows.append(sow)
    db.flush()

    # --- Gilts ---
    gilts = []
    for i in range(1, 5):
        g = Pig(
            ear_tag=f"GLT-{i:03d}",
            category=PigCategory.GILT,
            breed=random.choice(breeds),
            date_of_birth=today - timedelta(days=random.randint(200, 350)),
            weight_kg=round(random.uniform(100, 150), 1),
            pen_id=pens[6].id,
        )
        db.add(g)
        gilts.append(g)
    db.flush()

    # --- Finishers ---
    finishers = []
    for i in range(1, 21):
        f = Pig(
            ear_tag=f"FIN-{i:03d}",
            category=PigCategory.FINISHER,
            breed=random.choice(breeds),
            date_of_birth=today - timedelta(days=random.randint(90, 180)),
            weight_kg=round(random.uniform(50, 110), 1),
            pen_id=pens[4].id if i <= 10 else pens[5].id,
        )
        db.add(f)
        finishers.append(f)
    db.flush()

    # --- Piglets ---
    piglets = []
    for i in range(1, 31):
        p = Pig(
            ear_tag=f"PIG-{i:03d}",
            category=PigCategory.PIGLET,
            breed=random.choice(breeds),
            date_of_birth=today - timedelta(days=random.randint(1, 28)),
            weight_kg=round(random.uniform(1.2, 8.0), 1),
            pen_id=pens[2].id if i <= 15 else pens[3].id,
        )
        db.add(p)
        piglets.append(p)
    db.flush()

    # --- Health records ---
    statuses = list(HealthStatus)
    for pig in random.sample(sows + finishers + piglets, 15):
        hr = HealthRecord(
            pig_id=pig.id,
            status=random.choice(statuses),
            diagnosis=random.choice(["Respiratory", "Lameness", "Diarrhea", "Skin lesion", None]),
            treatment=random.choice(["Antibiotics 5d", "Anti-inflammatory", "Isolation", None]),
            vet_name=random.choice(["Dr. Petrović", "Dr. Jovanović", None]),
            record_date=today - timedelta(days=random.randint(0, 30)),
            next_checkup=today + timedelta(days=random.randint(3, 14)),
        )
        db.add(hr)

    # --- Farrowings ---
    for sow in sows[:5]:
        far = Farrowing(
            sow_id=sow.id,
            farrowing_date=today - timedelta(days=random.randint(5, 60)),
            live_born=random.randint(8, 14),
            stillborn=random.randint(0, 2),
            mummified=random.randint(0, 1),
            weaned_count=random.randint(7, 12),
            wean_date=today - timedelta(days=random.randint(0, 5)) if random.random() > 0.4 else None,
        )
        db.add(far)

    # --- Scan logs ---
    all_pigs = sows + gilts + finishers + piglets
    for pig in random.sample(all_pigs, min(20, len(all_pigs))):
        sl = ScanLog(
            pig_id=pig.id,
            raw_text=pig.ear_tag,
            parsed_tag=pig.ear_tag,
            source=ScanSource.EAR_TAG,
            confidence=round(random.uniform(0.75, 0.99), 2),
        )
        db.add(sl)

    db.commit()
    db.close()
    print(f"Seeded: 8 pens, {len(sows)} sows, {len(gilts)} gilts, "
          f"{len(finishers)} finishers, {len(piglets)} piglets + health/farrowing/scan data.")


if __name__ == "__main__":
    seed()
    