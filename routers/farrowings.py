"""CRUD router for Farrowings."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database.connection import get_db
from schemas.farrowing import FarrowingCreate, FarrowingRead, FarrowingUpdate
from services import farrowing_service

router = APIRouter(prefix="/farrowings", tags=["Farrowings"])


@router.get("/", response_model=list[FarrowingRead])
def list_farrowings(
    sow_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return farrowing_service.list_farrowings(db, sow_id=sow_id, skip=skip, limit=limit)


@router.get("/{farrowing_id}", response_model=FarrowingRead)
def get_farrowing(farrowing_id: int, db: Session = Depends(get_db)):
    far = farrowing_service.get_farrowing(db, farrowing_id)
    if not far:
        raise HTTPException(404, "Farrowing record not found")
    return far


@router.post("/", response_model=FarrowingRead, status_code=201)
def create_farrowing(data: FarrowingCreate, db: Session = Depends(get_db)):
    try:
        return farrowing_service.create_farrowing(db, data)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.patch("/{farrowing_id}", response_model=FarrowingRead)
def update_farrowing(farrowing_id: int, data: FarrowingUpdate, db: Session = Depends(get_db)):
    far = farrowing_service.update_farrowing(db, farrowing_id, data)
    if not far:
        raise HTTPException(404, "Farrowing record not found")
    return far
