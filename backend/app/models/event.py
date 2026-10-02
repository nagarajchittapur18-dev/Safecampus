"""SafeCampus AI — Event ORM Model"""

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Event(Base):
    """Campus events that influence crowd prediction."""

    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    location_id: Mapped[int] = mapped_column(Integer, ForeignKey("locations.id"), nullable=True)
    event_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    # Impact: low=0.25, medium=0.5, high=0.75, very_high=1.0
    impact_level: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    event_type: Mapped[str] = mapped_column(String(50), nullable=True)  # fest, exam, seminar, etc.
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    def __repr__(self) -> str:
        return f"<Event id={self.id} name={self.name!r} impact={self.impact_level}>"
