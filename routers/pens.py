"""CRUD router for Pens."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database.connection import get_db
from schemas.pen import PenCreate, PenRead, PenUpdate, PenOccupancy
from services import pen_service

router = APIRouter(prefix="/pens", tags=["Pens"])


@router.get("/", response_model=list[PenOccupancy])
def list_pens(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    pens = pen_service.list_pens(db, skip=skip, limit=limit)
    result = []
    for pen in pens:
        obj = PenOccupancy.model_validate(pen)
        obj.current_count = pen_service.get_occupancy(db, pen.id)
        result.append(obj)
    return result


@router.get("/{pen_id}", response_model=PenOccupancy)
def get_pen(pen_id: int, db: Session = Depends(get_db)):
    pen = pen_service.get_pen(db, pen_id)
    if not pen:
        raise HTTPException(404, "Pen not found")
    obj = PenOccupancy.model_validate(pen)
    obj.current_count = pen_service.get_occupancy(db, pen.id)
    return obj


@router.post("/", response_model=PenRead, status_code=201)
def create_pen(data: PenCreate, db: Session = Depends(get_db)):
    try:
        return pen_service.create_pen(db, data)
    except ValueError as e:
        raise HTTPException(409, str(e))


@router.patch("/{pen_id}", response_model=PenRead)
def update_pen(pen_id: int, data: PenUpdate, db: Session = Depends(get_db)):
    pen = pen_service.update_pen(db, pen_id, data)
    if not pen:
        raise HTTPException(404, "Pen not found")
    return pen
