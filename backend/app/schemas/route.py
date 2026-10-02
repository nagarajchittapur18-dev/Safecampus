"""
SafeCampus AI — Pydantic Schemas: Route Requests & Responses
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, model_validator


# ---------------------------------------------------------------------------
# Dijkstra request / response (Phase 3)
# ---------------------------------------------------------------------------

class DijkstraRequest(BaseModel):
    source_id: int = Field(..., gt=0, description="Start node ID")
    destination_id: int = Field(..., gt=0, description="End node ID")

    @model_validator(mode="after")
    def source_and_destination_differ(self) -> "DijkstraRequest":
        return self


class DijkstraResponse(BaseModel):
    source_id: int
    destination_id: int
    route: List[int] = Field(..., description="Ordered list of node IDs")
    route_names: List[str] = Field(..., description="Human-readable node names")
    distance_m: float = Field(..., description="Total path distance in metres")
    travel_time_min: float = Field(..., description="Estimated travel time in minutes")
    algorithm: str = "dijkstra"


# ---------------------------------------------------------------------------
# A* request / response (Phase 4)
# ---------------------------------------------------------------------------

class AStarRequest(BaseModel):
    source_id: int = Field(..., gt=0, description="Start node ID")
    destination_id: int = Field(..., gt=0, description="End node ID")

    @model_validator(mode="after")
    def validate_request(self) -> "AStarRequest":
        return self


class AStarResponse(BaseModel):
    source_id: int
    destination_id: int
    route: List[int] = Field(..., description="Ordered list of node IDs")
    route_names: List[str] = Field(..., description="Human-readable node names")
    distance_m: float = Field(..., description="Total path distance in metres")
    travel_time_min: float = Field(..., description="Estimated travel time in minutes")
    execution_time_ms: float = Field(..., description="Execution time in milliseconds")
    algorithm: str = "a_star"


# ---------------------------------------------------------------------------
# Personalized Multi-Objective Recommendation (Phase 5 & 7)
# ---------------------------------------------------------------------------

class RecommendRouteRequest(BaseModel):
    source_id: int = Field(..., gt=0, description="Start node ID")
    destination_id: int = Field(..., gt=0, description="End node ID")
    preference: str = Field(
        default="balanced",
        description="Route preference: shortest, fastest, safest, least_crowded, accessible, balanced"
    )
    weights: Optional[Dict[str, float]] = Field(
        default=None,
        description="Optional custom weights: {'wD': float, 'wT': float, 'wC': float, 'wS': float, 'wA': float}"
    )
    hour: Optional[int] = Field(default=None, ge=0, le=23, description="Hour of day (0-23)")
    day_of_week: Optional[int] = Field(default=None, ge=0, le=6, description="Day of week (0=Mon ... 6=Sun)")
    event_flag: int = Field(default=0, ge=0, le=1, description="1 if special event is active")
    class_activity: Optional[int] = Field(default=None, ge=0, le=1, description="1 if classes in session")
    exam_flag: int = Field(default=0, ge=0, le=1, description="1 if examination period")
    holiday_flag: int = Field(default=0, ge=0, le=1, description="1 if campus holiday")
    use_ml_crowd: bool = Field(default=True, description="Enable dynamic ML crowd prediction")


class MetricTradeoff(BaseModel):
    recommended: float = Field(..., description="Recommended route metric value")
    shortest: float = Field(..., description="Shortest baseline route metric value")
    difference: float = Field(..., description="Absolute difference: recommended - shortest")
    percentage_difference: float = Field(..., description="Relative percentage difference vs shortest")


class ShortestBaseline(BaseModel):
    route: List[int] = Field(..., description="Node IDs along shortest route")
    route_names: List[str] = Field(..., description="Node names along shortest route")
    distance_m: float = Field(..., description="Shortest path distance in metres")
    travel_time_min: float = Field(..., description="Shortest path travel time in minutes")
    crowd_score: float = Field(..., description="Average crowd score along shortest path")
    crowd_level: str = Field(..., description="Discrete crowd category on shortest path")
    safety_score: float = Field(..., description="Average safety score along shortest path")
    accessibility_score: float = Field(..., description="Average accessibility score along shortest path")


class RouteExplanation(BaseModel):
    summary: str = Field(..., description="Concise rationale, e.g. 'Recommended because predicted crowd is low and the route has a high safety score.'")
    why_selected: str = Field(..., description="Comprehensive explanation of why this specific route was selected")
    distance_tradeoff: str = Field(..., description="Dynamic narrative of distance trade-off vs shortest route")
    time_tradeoff: str = Field(..., description="Dynamic narrative of time trade-off vs shortest route")
    crowd_tradeoff: str = Field(..., description="Dynamic narrative of crowd trade-off vs shortest route")
    safety_tradeoff: str = Field(..., description="Dynamic narrative of safety trade-off vs shortest route")
    accessibility_tradeoff: str = Field(..., description="Dynamic narrative of accessibility trade-off vs shortest route")
    reasons: List[str] = Field(default_factory=list, description="Key dynamic reasoning points")
    tradeoffs: Dict[str, Any] = Field(..., description="Quantified metric deltas against the shortest path")
    shortest_baseline: ShortestBaseline = Field(..., description="Shortest route baseline metrics")


class AlternativeRoute(BaseModel):
    label: str = Field(..., description="Human-readable route label, e.g. 'Shortest Path'")
    preference: str = Field(..., description="Preference preset used for this alternative")
    route: List[int] = Field(..., description="Ordered list of node IDs")
    route_names: List[str] = Field(..., description="Human-readable node names")
    distance_m: float = Field(..., description="Total route distance in metres")
    travel_time_min: float = Field(..., description="Total route travel time in minutes")
    crowd_score: float = Field(..., description="Average crowd density score [0, 1]")
    crowd_level: str = Field(..., description="Discrete crowd level (LOW, MEDIUM, HIGH, VERY_HIGH)")
    safety_score: float = Field(..., description="Average safety score [0, 1]")
    accessibility_score: float = Field(..., description="Average accessibility score [0, 1]")
    total_cost: float = Field(..., description="Total multi-objective cost")


class RecommendRouteResponse(BaseModel):
    source_id: int
    destination_id: int
    preference: str
    weights: Dict[str, float]
    route: List[int] = Field(..., description="Ordered node path")
    recommended_route: List[int] = Field(..., description="Alias for route")
    route_names: List[str] = Field(..., description="Human-readable location names")
    distance_m: float = Field(..., description="Total route distance in metres")
    travel_time_min: float = Field(..., description="Total route travel time in minutes")
    crowd_score: float = Field(..., description="Average crowd density exposure [0, 1]")
    crowd_level: str = Field(..., description="Discrete crowd category: LOW, MEDIUM, HIGH, VERY_HIGH")
    safety_score: float = Field(..., description="Average safety score [0, 1]")
    accessibility_score: float = Field(..., description="Average accessibility score [0, 1]")
    total_cost: float = Field(..., description="Total multi-objective cost")
    execution_time_ms: float = Field(..., description="Execution duration in milliseconds")
    algorithm: str = "personalized_multi_objective_a_star"
    used_ml_crowd: bool = Field(True, description="Indicates whether dynamic ML predictions were used")
    model_name: Optional[str] = Field(None, description="Name of the ML model supplying predictions")
    alternatives: List[AlternativeRoute] = Field(default_factory=list, description="Candidate alternative routes")
    explanation: Optional[RouteExplanation] = Field(None, description="Dynamic explanation and trade-off analysis")


class ExplainRouteResponse(BaseModel):
    source_id: int
    destination_id: int
    preference: str
    explanation: RouteExplanation
    recommendation: RecommendRouteResponse


