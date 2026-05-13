"""SQLAlchemy ORM models for FarmaTrack."""

from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, Float, Date, DateTime,
    ForeignKey, Text, Enum, Boolean,
)
from sqlalchemy.orm import relationship, DeclarativeBase

from database.enums import PigCategory, HealthStatus, ScanSource


class Base(DeclarativeBase):
    pass


class Pen(Base):
    __tablename__ = "pens"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    capacity = Column(Integer, nullable=False, default=20)
    pen_type = Column(String(50), nullable=True)  # e.g. farrowing, nursery, finishing
    created_at = Column(DateTime, default=datetime.utcnow)

    pigs = relationship("Pig", back_populates="pen")


class Pig(Base):
    __tablename__ = "pigs"

    id = Column(Integer, primary_key=True, index=True)
    ear_tag = Column(String(30), unique=True, nullable=False, index=True)
    category = Column(Enum(PigCategory), nullable=False)
    breed = Column(String(80), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    weight_kg = Column(Float, nullable=True)
    pen_id = Column(Integer, ForeignKey("pens.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    pen = relationship("Pen", back_populates="pigs")
    health_records = relationship("HealthRecord", back_populates="pig", cascade="all, delete-orphan")
    farrowings = relationship("Farrowing", back_populates="sow", cascade="all, delete-orphan")
    scans = relationship("ScanLog", back_populates="pig", cascade="all, delete-orphan")


class HealthRecord(Base):
    __tablename__ = "health_records"

    id = Column(Integer, primary_key=True, index=True)
    pig_id = Column(Integer, ForeignKey("pigs.id"), nullable=False)
    status = Column(Enum(HealthStatus), nullable=False, default=HealthStatus.HEALTHY)
    diagnosis = Column(String(200), nullable=True)
    treatment = Column(Text, nullable=True)
    vet_name = Column(String(100), nullable=True)
    record_date = Column(Date, default=date.today)
    next_checkup = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    pig = relationship("Pig", back_populates="health_records")


class Farrowing(Base):
    __tablename__ = "farrowings"

    id = Column(Integer, primary_key=True, index=True)
    sow_id = Column(Integer, ForeignKey("pigs.id"), nullable=False)
    insemination_date = Column(Date, nullable=True)
    farrowing_date = Column(Date, nullable=True)
    live_born = Column(Integer, nullable=True)
    stillborn = Column(Integer, nullable=False, default=0)
    mummified = Column(Integer, nullable=False, default=0)
    weaned_count = Column(Integer, nullable=True)
    wean_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    sow = relationship("Pig", back_populates="farrowings")

    @property
    def expected_farrowing_date(self):
        from datetime import timedelta
        return (self.insemination_date + timedelta(days=114)) if self.insemination_date else None

    @property
    def total_born(self) -> int:
        return (self.live_born or 0) + self.stillborn + self.mummified


class ScanLog(Base):
    __tablename__ = "scan_logs"

    id = Column(Integer, primary_key=True, index=True)
    pig_id = Column(Integer, ForeignKey("pigs.id"), nullable=True)
    raw_text = Column(Text, nullable=False)
    parsed_tag = Column(String(50), nullable=True)
    source = Column(Enum(ScanSource), default=ScanSource.EAR_TAG)
    confidence = Column(Float, nullable=True)
    scanned_at = Column(DateTime, default=datetime.utcnow)

    pig = relationship("Pig", back_populates="scans")
