"""SafeCampus AI — Route ORM Model"""

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Route(Base):
    """Stores a computed route recommendation for history / analytics."""

    __tablename__ = "routes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    source_id: Mapped[int] = mapped_column(Integer, ForeignKey("locations.id"), nullable=False)
    destination_id: Mapped[int] = mapped_column(Integer, ForeignKey("locations.id"), nullable=False)
    preference: Mapped[str] = mapped_column(String(30), nullable=False, default="balanced")
    algorithm: Mapped[str] = mapped_column(String(50), nullable=False, default="multi_objective_astar")

    # Computed metrics
    distance_m: Mapped[float] = mapped_column(Float, nullable=True)
    travel_time_min: Mapped[float] = mapped_column(Float, nullable=True)
    safety_score: Mapped[float] = mapped_column(Float, nullable=True)
    accessibility_score: Mapped[float] = mapped_column(Float, nullable=True)
    total_cost: Mapped[float] = mapped_column(Float, nullable=True)

    # Serialised route path (JSON string of node IDs)
    route_path: Mapped[str] = mapped_column(Text, nullable=True)
    explanation: Mapped[str] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    def __repr__(self) -> str:
        return f"<Route id={self.id} {self.source_id}→{self.destination_id} pref={self.preference!r}>"
