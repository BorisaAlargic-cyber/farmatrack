"""FarmaTrack — direct service client.

Replaces the HTTP-based api_client for Streamlit Cloud deployment.
All dashboard pages call this module unchanged — same function signatures,
no FastAPI/HTTP layer needed.
"""

import os
import tempfile
from contextlib import contextmanager
from typing import Optional

from database.enums import ScanSource
from schemas.pig import PigCreate, PigUpdate, PigRead
from schemas.pen import PenCreate, PenUpdate, PenOccupancy
from schemas.health import HealthRecordCreate, HealthRecordUpdate, HealthRecordRead
from schemas.farrowing import FarrowingCreate, FarrowingUpdate, FarrowingRead
from schemas.scan import ScanRequest, ScanResult, ScanLogRead
from services import pig_service, pen_service, health_service, farrowing_service, scan_service
from services.dashboard_service import get_summary as _get_summary
from scanner.ocr import ocr_image


@contextmanager
def _db():
    from database.connection import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Dashboard ──────────────────────────────────────────────
def get_summary() -> dict:
    with _db() as db:
        return _get_summary(db)


# ── Pigs ───────────────────────────────────────────────────
def list_pigs(category: Optional[str] = None, pen_id: Optional[int] = None, active_only: bool = True) -> list[dict]:
    with _db() as db:
        pigs = pig_service.list_pigs(db, category=category, pen_id=pen_id, active_only=active_only)
        return [PigRead.model_validate(p).model_dump(mode="json") for p in pigs]


def get_pig(pig_id: int) -> dict:
    with _db() as db:
        pig = pig_service.get_pig(db, pig_id)
        if not pig:
            raise RuntimeError(f"Pig {pig_id} not found")
        return PigRead.model_validate(pig).model_dump(mode="json")


def create_pig(data: dict) -> dict:
    with _db() as db:
        if pig_service.get_pig_by_tag(db, data["ear_tag"]):
            raise RuntimeError(f"Ear tag '{data['ear_tag']}' already exists")
        pig = pig_service.create_pig(db, PigCreate(**data))
        return PigRead.model_validate(pig).model_dump(mode="json")


def update_pig(pig_id: int, data: dict) -> dict:
    with _db() as db:
        pig = pig_service.update_pig(db, pig_id, PigUpdate(**data))
        if not pig:
            raise RuntimeError(f"Pig {pig_id} not found")
        return PigRead.model_validate(pig).model_dump(mode="json")


def deactivate_pig(pig_id: int) -> dict:
    with _db() as db:
        pig = pig_service.deactivate_pig(db, pig_id)
        if not pig:
            raise RuntimeError(f"Pig {pig_id} not found")
        return PigRead.model_validate(pig).model_dump(mode="json")


# ── Pens ───────────────────────────────────────────────────
def list_pens() -> list[dict]:
    with _db() as db:
        pens = pen_service.list_pens(db)
        result = []
        for p in pens:
            obj = PenOccupancy.model_validate(p)
            obj.current_count = pen_service.get_occupancy(db, p.id)
            result.append(obj.model_dump(mode="json"))
        return result


def create_pen(data: dict) -> dict:
    with _db() as db:
        try:
            pen = pen_service.create_pen(db, PenCreate(**data))
            obj = PenOccupancy.model_validate(pen)
            obj.current_count = 0
            return obj.model_dump(mode="json")
        except ValueError as e:
            raise RuntimeError(str(e))


def update_pen(pen_id: int, data: dict) -> dict:
    with _db() as db:
        pen = pen_service.update_pen(db, pen_id, PenUpdate(**data))
        if not pen:
            raise RuntimeError(f"Pen {pen_id} not found")
        obj = PenOccupancy.model_validate(pen)
        obj.current_count = pen_service.get_occupancy(db, pen_id)
        return obj.model_dump(mode="json")


# ── Health ─────────────────────────────────────────────────
def list_health_records(pig_id: Optional[int] = None) -> list[dict]:
    with _db() as db:
        recs = health_service.list_health_records(db, pig_id=pig_id)
        return [HealthRecordRead.model_validate(r).model_dump(mode="json") for r in recs]


def create_health_record(data: dict) -> dict:
    with _db() as db:
        try:
            rec = health_service.create_health_record(db, HealthRecordCreate(**data))
            return HealthRecordRead.model_validate(rec).model_dump(mode="json")
        except ValueError as e:
            raise RuntimeError(str(e))


def update_health_record(record_id: int, data: dict) -> dict:
    with _db() as db:
        rec = health_service.update_health_record(db, record_id, HealthRecordUpdate(**data))
        if not rec:
            raise RuntimeError(f"Health record {record_id} not found")
        return HealthRecordRead.model_validate(rec).model_dump(mode="json")


def delete_health_record(record_id: int):
    with _db() as db:
        if not health_service.delete_health_record(db, record_id):
            raise RuntimeError(f"Health record {record_id} not found")


# ── Farrowings ─────────────────────────────────────────────
def list_farrowings(sow_id: Optional[int] = None) -> list[dict]:
    with _db() as db:
        rows = farrowing_service.list_farrowings(db, sow_id=sow_id)
        return [FarrowingRead.model_validate(f).model_dump(mode="json") for f in rows]


def create_farrowing(data: dict) -> dict:
    with _db() as db:
        try:
            far = farrowing_service.create_farrowing(db, FarrowingCreate(**data))
            return FarrowingRead.model_validate(far).model_dump(mode="json")
        except ValueError as e:
            raise RuntimeError(str(e))


def update_farrowing(farrowing_id: int, data: dict) -> dict:
    with _db() as db:
        far = farrowing_service.update_farrowing(db, farrowing_id, FarrowingUpdate(**data))
        if not far:
            raise RuntimeError(f"Farrowing {farrowing_id} not found")
        return FarrowingRead.model_validate(far).model_dump(mode="json")


# ── Scan ───────────────────────────────────────────────────
def scan_text(raw_text: str, source: str = "ear_tag") -> dict:
    with _db() as db:
        req = ScanRequest(raw_text=raw_text, source=ScanSource(source))
        result = scan_service.process_scan(db, req)
        return result.model_dump(mode="json")


def scan_image(file_bytes: bytes, filename: str) -> dict:
    suffix = os.path.splitext(filename or ".jpg")[1] or ".jpg"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name
    try:
        raw_text = ocr_image(tmp_path)
        if not raw_text:
            return ScanResult(message="OCR could not extract text from the image.").model_dump(mode="json")
        return scan_text(raw_text, source="ear_tag")
    finally:
        os.unlink(tmp_path)


def list_scan_logs() -> list[dict]:
    with _db() as db:
        logs = scan_service.list_scans(db)
        return [ScanLogRead.model_validate(l).model_dump(mode="json") for l in logs]
