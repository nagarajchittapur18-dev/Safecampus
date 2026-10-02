"""
SafeCampus AI — Campus Graph Domain Models
==========================================
Pure Python dataclasses — no ORM dependency.
These are the in-memory graph structures used by all routing algorithms.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional


# ---------------------------------------------------------------------------
# Node
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Node:
    """Represents a campus location (building, gate, junction, etc.)."""

    id: int
    name: str
    latitude: float
    longitude: float
    node_type: str           # gate | building | junction | lab | library | …
    description: str = ""

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def distance_to(self, other: "Node") -> float:
        """
        Euclidean / spherical distance in metres between two nodes, derived from
        latitude/longitude using the Haversine formula.
        """
        return haversine_metres(
            self.latitude, self.longitude,
            other.latitude, other.longitude,
        )

    def __str__(self) -> str:
        return f"Node({self.id}, {self.name!r}, type={self.node_type!r})"


# ---------------------------------------------------------------------------
# Edge
# ---------------------------------------------------------------------------

@dataclass
class Edge:
    """Represents a directed walkable path between two campus nodes."""

    id: int
    source: int                 # Node ID
    destination: int            # Node ID
    distance: float             # Metres
    base_time: float            # Minutes (unloaded travel time)
    safety_score: float         # 0.0 (unsafe) → 1.0 (very safe)
    accessibility_score: float  # 0.0 (inaccessible) → 1.0 (fully accessible)
    stairs: bool                # True if the path includes stairs
    ramp_available: bool        # True if a ramp/lift alternative exists
    crowd_score: float = 0.5    # 0.0 (empty) → 1.0 (heavily crowded) [placeholder]
    note: str = ""

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def __post_init__(self) -> None:
        if not (0.0 <= self.safety_score <= 1.0):
            raise ValueError(
                f"Edge {self.id}: safety_score {self.safety_score} not in [0, 1]"
            )
        if not (0.0 <= self.accessibility_score <= 1.0):
            raise ValueError(
                f"Edge {self.id}: accessibility_score {self.accessibility_score} not in [0, 1]"
            )
        if not (0.0 <= self.crowd_score <= 1.0):
            raise ValueError(
                f"Edge {self.id}: crowd_score {self.crowd_score} not in [0, 1]"
            )
        if self.distance <= 0:
            raise ValueError(
                f"Edge {self.id}: distance must be positive, got {self.distance}"
            )
        if self.base_time <= 0:
            raise ValueError(
                f"Edge {self.id}: base_time must be positive, got {self.base_time}"
            )

    def reversed(self) -> "Edge":
        """
        Return a new Edge in the opposite direction.

        Used when loading bidirectional edges from JSON.
        The edge ID for the reversed copy uses negative sign convention
        (e.g., edge 5 reversed → id=-5) so IDs remain unique within the graph.
        Attributes are symmetrical (same distance, safety, etc.).
        """
        return Edge(
            id=-self.id,
            source=self.destination,
            destination=self.source,
            distance=self.distance,
            base_time=self.base_time,
            safety_score=self.safety_score,
            accessibility_score=self.accessibility_score,
            stairs=self.stairs,
            ramp_available=self.ramp_available,
            crowd_score=self.crowd_score,
            note=f"{self.note} [reversed]",
        )

    def __str__(self) -> str:
        return (
            f"Edge({self.source}→{self.destination}, "
            f"dist={self.distance}m, safety={self.safety_score:.2f}, "
            f"access={self.accessibility_score:.2f}, crowd={self.crowd_score:.2f})"
        )


# ---------------------------------------------------------------------------
# Haversine helper
# ---------------------------------------------------------------------------

def haversine_metres(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Compute the great-circle distance between two WGS-84 coordinates in metres.
    Accurate to within ~0.5% for distances up to a few kilometres.
    """
    R = 6_371_000  # Earth radius in metres
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))
