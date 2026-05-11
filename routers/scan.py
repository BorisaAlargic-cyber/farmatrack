"""Scan endpoint — OCR or manual ear-tag lookup."""

from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session

from database.connection import get_db
from database.enums import ScanSource
from schemas.scan import ScanRequest, ScanResult, ScanLogRead
from services.scan_service import process_scan, list_scans
from scanner.ocr import ocr_image

import tempfile, os

router = APIRouter(prefix="/scan", tags=["Scan"])


@router.post("/", response_model=ScanResult)
def scan_tag(data: ScanRequest, db: Session = Depends(get_db)):
    """Process a manual text scan."""
    return process_scan(db, data)


@router.post("/image", response_model=ScanResult)
async def scan_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload an ear-tag image, run OCR, and look up the pig."""
    suffix = os.path.splitext(file.filename or ".png")[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        raw_text = ocr_image(tmp_path)
        if not raw_text:
            return ScanResult(message="OCR could not extract text from the image.")
        req = ScanRequest(raw_text=raw_text, source=ScanSource.EAR_TAG)
        return process_scan(db, req)
    finally:
        os.unlink(tmp_path)


@router.get("/logs", response_model=list[ScanLogRead])
def get_scan_logs(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return list_scans(db, skip=skip, limit=limit)
