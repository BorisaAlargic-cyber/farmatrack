"""Database engine, session factory, and dependency."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from typing import Generator, Optional

engine = None
SessionLocal = None


def init_db(database_url: Optional[str] = None) -> None:
    """Create engine, session factory, and all tables.

    database_url is passed directly from st.secrets in dashboard/app.py,
    bypassing env vars entirely so Streamlit Cloud secrets always win.
    Falls back to SQLite for local development.
    """
    global engine, SessionLocal

    if database_url is None:
        from config import get_settings
        database_url = get_settings().DATABASE_URL

    _is_sqlite = "sqlite" in database_url

    if _is_sqlite:
        engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False},
        )
    else:
        engine = create_engine(
            database_url,
            poolclass=NullPool,
        )

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    from database.models import Base
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency — yields a DB session and closes it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
