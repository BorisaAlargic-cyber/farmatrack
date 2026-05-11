"""Database engine, session factory, and dependency."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool, StaticPool
from typing import Generator

from config import get_settings

settings = get_settings()

_is_sqlite = "sqlite" in settings.DATABASE_URL

if _is_sqlite:
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=settings.DEBUG,
    )
else:
    # NullPool: let pgBouncer (Transaction Pooler) handle connection pooling.
    # pool_pre_ping: discard stale connections silently.
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"sslmode": "require"},
        poolclass=NullPool,
        pool_pre_ping=True,
        echo=settings.DEBUG,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Create all tables if they don't exist."""
    from database.models import Base
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency — yields a DB session and closes it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
