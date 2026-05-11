"""CRUD router for Pigs."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database.connection import get_db
from database.enums import PigCategory
from schemas.pig import PigCreate, PigRead, PigUpdate
from services import pig_service

router = APIRouter(prefix="/pigs", tags=["Pigs"])


@router.get("/", response_model=list[PigRead])
def list_pigs(
    category: Optional[PigCategory] = None,
    pen_id: Optional[int] = None,
    active_only: bool = True,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return pig_service.list_pigs(
        db, category=category, pen_id=pen_id, active_only=active_only, skip=skip, limit=limit,
    )


@router.get("/{pig_id}", response_model=PigRead)
def get_pig(pig_id: int, db: Session = Depends(get_db)):
    pig = pig_service.get_pig(db, pig_id)
    if not pig:
        raise HTTPException(404, "Pig not found")
    return pig


@router.post("/", response_model=PigRead, status_code=201)
def create_pig(data: PigCreate, db: Session = Depends(get_db)):
    existing = pig_service.get_pig_by_tag(db, data.ear_tag)
    if existing:
        raise HTTPException(409, f"Ear tag '{data.ear_tag}' already exists")
    return pig_service.create_pig(db, data)


@router.patch("/{pig_id}", response_model=PigRead)
def update_pig(pig_id: int, data: PigUpdate, db: Session = Depends(get_db)):
    pig = pig_service.update_pig(db, pig_id, data)
    if not pig:
        raise HTTPException(404, "Pig not found")
    return pig


@router.delete("/{pig_id}", response_model=PigRead)
def deactivate_pig(pig_id: int, db: Session = Depends(get_db)):
    pig = pig_service.deactivate_pig(db, pig_id)
    if not pig:
        raise HTTPException(404, "Pig not found")
    return pig
