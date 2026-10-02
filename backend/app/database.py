"""
SafeCampus AI — SQLite + SQLAlchemy Configuration
==================================================
Uses async SQLAlchemy with aiosqlite driver.
Database file: backend/campus.db
"""

import os
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

# ---------------------------------------------------------------------------
# Database URL
# ---------------------------------------------------------------------------

# Resolve path relative to this file so it works regardless of CWD
_BASE_DIR = Path(__file__).resolve().parent.parent
_DB_PATH = os.environ.get("DATABASE_URL", f"sqlite+aiosqlite:///{_BASE_DIR / 'campus.db'}")

# ---------------------------------------------------------------------------
# Engine & session factory
# ---------------------------------------------------------------------------

engine = create_async_engine(
    _DB_PATH,
    echo=False,          # Set True to log SQL statements during development
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ---------------------------------------------------------------------------
# Declarative base (all ORM models inherit from this)
# ---------------------------------------------------------------------------

class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def init_db() -> None:
    """Create all tables defined by ORM models."""
    # Import models so they register with Base.metadata
    from app.models import user, location, route, event  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    """FastAPI dependency: yields an async DB session."""
    async with AsyncSessionLocal() as session:
        yield session
