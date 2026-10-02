"""
SafeCampus AI — Personalized Multi-Objective A* Algorithm
==========================================================
The core research algorithm of SafeCampus AI.

Finds the Pareto-optimal route minimizing the multi-objective cost:

    Cost(e) = wD * D(e) + wT * T(e) + wC * C(e) + wS * S(e) + wA * A(e)

where:
    wD + wT + wC + wS + wA = 1.0   (configurable weight vector)
    D(e) = normalized distance in [0, 1]
    T(e) = normalized travel time in [0, 1]
    C(e) = normalized crowd cost in [0, 1] (dynamically predicted by ML model or fallback)
    S(e) = normalized safety cost in [0, 1]       (1.0 - safety_score)
    A(e) = normalized accessibility cost in [0, 1] (1.0 - accessibility_score)

And for a route R:
    Cost(R) = sum(Cost(e) for e in R)
    R* = argmin Cost(R)

Admissible Heuristic
--------------------
Because Cost(e) >= wD * (d(e) / D_max) for non-negative weights and costs,
the scaled geographic Haversine distance:
    h(u) = wD * (haversine(u, dest) / D_max)
is strictly admissible (h(u) <= Cost*(u, dest)) and monotonic (consistent).
"""

from __future__ import annotations

import heapq
import math
import time
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional, Tuple

from app.algorithms.dijkstra import NodeNotFoundError, NoPathError
from app.algorithms.graph import CampusGraph
from app.algorithms.models import Edge, Node


# ---------------------------------------------------------------------------
# WeightVector
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class WeightVector:
    """
    Configurable weight vector for multi-objective cost evaluation.
    All weights must be non-negative and sum to 1.0 within epsilon tolerance.
    """

    wD: float  # Distance weight
    wT: float  # Travel time weight
    wC: float  # Crowd density weight
    wS: float  # Safety weight
    wA: float  # Accessibility weight

    PRESETS = {
        "shortest": {
            "wD": 0.70, "wT": 0.10, "wC": 0.05, "wS": 0.10, "wA": 0.05
        },
        "fastest": {
            "wD": 0.10, "wT": 0.70, "wC": 0.05, "wS": 0.10, "wA": 0.05
        },
        "safest": {
            "wD": 0.10, "wT": 0.05, "wC": 0.05, "wS": 0.70, "wA": 0.10
        },
        "least_crowded": {
            "wD": 0.10, "wT": 0.05, "wC": 0.70, "wS": 0.10, "wA": 0.05
        },
        "accessible": {
            "wD": 0.10, "wT": 0.05, "wC": 0.05, "wS": 0.10, "wA": 0.70
        },
        "balanced": {
            "wD": 0.20, "wT": 0.20, "wC": 0.20, "wS": 0.20, "wA": 0.20
        },
    }

    def __post_init__(self) -> None:
        weights = [self.wD, self.wT, self.wC, self.wS, self.wA]
        for w, name in zip(weights, ["wD", "wT", "wC", "wS", "wA"]):
            if w < 0.0:
                raise ValueError(f"Weight {name} must be non-negative, got {w}")

        total = sum(weights)
        if abs(total - 1.0) > 1e-4:
            raise ValueError(
                f"Weights must sum to 1.0 (wD+wT+wC+wS+wA = {total:.6f})"
            )

    @classmethod
    def from_preference(cls, preference: str) -> "WeightVector":
        """
        Instantiate a WeightVector from a standard preference string preset.
        Supported presets: shortest, fastest, safest, least_crowded, accessible, balanced.
        """
        normalized = preference.strip().lower().replace("-", "_").replace(" ", "_")
        if normalized not in cls.PRESETS:
            valid = list(cls.PRESETS.keys())
            raise ValueError(
                f"Unknown preference preset {preference!r}. Valid options: {valid}"
            )
        return cls(**cls.PRESETS[normalized])

    def to_dict(self) -> Dict[str, float]:
        return asdict(self)


# ---------------------------------------------------------------------------
# MultiObjectiveResult
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class MultiObjectiveResult:
    """Immutable result from multi_objective_a_star()."""

    source_id: int
    destination_id: int
    path: List[int]
    total_cost: float
    distance_m: float
    travel_time_min: float
    crowd_score: float                  # Average crowd exposure [0, 1]
    crowd_level: str                    # LOW / MEDIUM / HIGH / VERY_HIGH
    safety_score: float                 # Average safety score [0, 1]
    accessibility_score: float          # Average accessibility score [0, 1]
    execution_time_ms: float
    preference: str
    weights: Dict[str, float]
    used_ml_crowd: bool = False         # True if dynamic ML predictions were used
    model_name: Optional[str] = None    # Name of the predictive model used

    @property
    def reachable(self) -> bool:
        return len(self.path) > 0

    def __str__(self) -> str:
        if not self.reachable:
            return f"MultiObjectiveResult: no path from {self.source_id} to {self.destination_id}"
        ml_tag = f" [ML: {self.model_name}]" if self.used_ml_crowd else " [Baseline Crowd]"
        return (
            f"MultiObjectiveResult({self.preference}{ml_tag}): "
            f"{' → '.join(str(n) for n in self.path)} | "
            f"cost={self.total_cost:.4f} | dist={self.distance_m:.1f}m | "
            f"time={self.travel_time_min:.2f}min | safety={self.safety_score:.2f} | "
            f"crowd={self.crowd_score:.2f} ({self.crowd_level}) | "
            f"access={self.accessibility_score:.2f} | {self.execution_time_ms:.3f}ms"
        )


# ---------------------------------------------------------------------------
# Helper: Crowd Level Categorization
# ---------------------------------------------------------------------------

def crowd_score_to_level(score: float) -> str:
    """Categorizes a normalized crowd score in [0, 1] into a discrete level."""
    if score < 0.28:
        return "LOW"
    elif score < 0.52:
        return "MEDIUM"
    elif score < 0.74:
        return "HIGH"
    else:
        return "VERY_HIGH"


# ---------------------------------------------------------------------------
# Helper: Edge Cost Evaluation
# ---------------------------------------------------------------------------

def calculate_edge_cost(
    graph: CampusGraph,
    edge: Edge,
    weights: WeightVector,
    crowd_cost: Optional[float] = None,
) -> float:
    """
    Computes the normalized multi-objective cost for a single edge:
        Cost(e) = wD*D + wT*T + wC*C + wS*S + wA*A
    Each factor is guaranteed in [0, 1], so Cost(e) in [0, 1].

    Parameters
    ----------
    graph      : CampusGraph instance.
    edge       : Edge instance.
    weights    : WeightVector with weights summing to 1.0.
    crowd_cost : Optional dynamic predicted crowd cost in [0, 1].
                 If None, falls back to static edge.crowd_score.
    """
    D = graph.normalize_distance(edge.distance)
    T = graph.normalize_time(edge.base_time)
    C = crowd_cost if crowd_cost is not None else edge.crowd_score
    S = 1.0 - edge.safety_score

    # Accessibility cost: 1.0 - accessibility_score
    # If edge has stairs and no ramp, it incurs full accessibility cost (1.0)
    if edge.stairs and not edge.ramp_available:
        A = 1.0
    else:
        A = 1.0 - edge.accessibility_score

    # Clamp each component to [0, 1]
    D = max(0.0, min(1.0, D))
    T = max(0.0, min(1.0, T))
    C = max(0.0, min(1.0, C))
    S = max(0.0, min(1.0, S))
    A = max(0.0, min(1.0, A))

    return (
        weights.wD * D +
        weights.wT * T +
        weights.wC * C +
        weights.wS * S +
        weights.wA * A
    )


# ---------------------------------------------------------------------------
# Algorithm
# ---------------------------------------------------------------------------

def multi_objective_a_star(
    graph: CampusGraph,
    source_id: int,
    destination_id: int,
    weights: Optional[WeightVector] = None,
    preference: str = "balanced",
    node_crowd_scores: Optional[Dict[int, float]] = None,
    model_name: Optional[str] = None,
) -> MultiObjectiveResult:
    """
    Personalized Multi-Objective A* routing with optional dynamic ML crowd integration.

    Parameters
    ----------
    graph             : CampusGraph instance.
    source_id         : Start node ID.
    destination_id    : Target node ID.
    weights           : Optional WeightVector. If omitted, derived from `preference`.
    preference        : Name of preference preset ('balanced', 'safest', etc.).
    node_crowd_scores : Optional dict of {location_id: predicted_crowd_score [0, 1]}.
                        If provided, dynamically replaces static edge crowd baselines.
                        If None, uses edge.crowd_score as fallback.
    model_name        : Name of the ML model supplying predictions (for provenance).

    Returns
    -------
    MultiObjectiveResult with path, total_cost, component scores, and metadata.
    """
    start_time = time.perf_counter()

    # ---- Validation ----
    errors = []
    if not graph.has_node(source_id):
        errors.append(f"Source node {source_id!r} not found in campus graph.")
    if not graph.has_node(destination_id):
        errors.append(f"Destination node {destination_id!r} not found in campus graph.")
    if errors:
        raise NodeNotFoundError(" | ".join(errors))

    # Resolve weights
    if weights is None:
        weights = WeightVector.from_preference(preference)

    used_ml_crowd = node_crowd_scores is not None and len(node_crowd_scores) > 0

    # ---- Same source and destination ----
    if source_id == destination_id:
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        start_crowd = (
            node_crowd_scores.get(source_id, 0.0)
            if node_crowd_scores
            else 0.0
        )
        return MultiObjectiveResult(
            source_id=source_id,
            destination_id=destination_id,
            path=[source_id],
            total_cost=0.0,
            distance_m=0.0,
            travel_time_min=0.0,
            crowd_score=round(start_crowd, 4),
            crowd_level=crowd_score_to_level(start_crowd),
            safety_score=1.0,
            accessibility_score=1.0,
            execution_time_ms=round(elapsed_ms, 3),
            preference=preference,
            weights=weights.to_dict(),
            used_ml_crowd=used_ml_crowd,
            model_name=model_name if used_ml_crowd else None,
        )

    dest_node = graph.get_node(destination_id)
    assert dest_node is not None

    # Max distance for heuristic normalization
    max_d = graph._max_distance if graph._max_distance > 0 else 1.0

    def heuristic(u_id: int) -> float:
        """
        Admissible heuristic:
            h(u) = wD * (haversine(u, dest) / max_distance)
        """
        if weights.wD <= 0.0:
            return 0.0
        u_node = graph.get_node(u_id)
        if u_node is None:
            return 0.0
        h_meters = u_node.distance_to(dest_node)
        return weights.wD * (h_meters / max_d)

    def get_edge_crowd(e: Edge) -> float:
        """Retrieves dynamic ML crowd cost or falls back to static edge baseline."""
        if node_crowd_scores is not None:
            src_c = node_crowd_scores.get(e.source)
            dst_c = node_crowd_scores.get(e.destination)
            if src_c is not None and dst_c is not None:
                return 0.5 * (src_c + dst_c)
            elif dst_c is not None:
                return dst_c
            elif src_c is not None:
                return src_c
        return e.crowd_score

    # ---- Initialise search data structures ----
    g_cost: Dict[int, float] = {n.id: math.inf for n in graph.all_nodes()}
    g_cost[source_id] = 0.0

    # Edge tracking to compute exact component scores along the final path
    edge_taken: Dict[int, Optional[Edge]] = {n.id: None for n in graph.all_nodes()}
    edge_crowd_used: Dict[int, float] = {}
    prev: Dict[int, Optional[int]] = {n.id: None for n in graph.all_nodes()}

    counter = 0
    h_start = heuristic(source_id)
    open_set: List[Tuple[float, int, int]] = [(h_start, counter, source_id)]
    closed_set: set[int] = set()

    found = False

    # ---- Priority Queue Loop ----
    while open_set:
        current_f, _, u = heapq.heappop(open_set)

        if u in closed_set:
            continue
        closed_set.add(u)

        if u == destination_id:
            found = True
            break

        current_g = g_cost[u]

        for edge in graph.neighbors(u):
            v = edge.destination
            if v in closed_set:
                continue

            crowd_c = get_edge_crowd(edge)
            cost_e = calculate_edge_cost(graph, edge, weights, crowd_cost=crowd_c)
            tentative_g = current_g + cost_e

            if tentative_g < g_cost[v]:
                g_cost[v] = tentative_g
                prev[v] = u
                edge_taken[v] = edge
                edge_crowd_used[v] = crowd_c

                counter += 1
                f_v = tentative_g + heuristic(v)
                heapq.heappush(open_set, (f_v, counter, v))

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    if not found or math.isinf(g_cost[destination_id]):
        raise NoPathError(
            f"No path from node {source_id} to node {destination_id} "
            f"in the campus graph."
        )

    # ---- Reconstruct path and aggregate metrics ----
    path: List[int] = []
    edges_in_path: List[Edge] = []
    crowds_in_path: List[float] = []
    curr: Optional[int] = destination_id

    while curr is not None:
        path.append(curr)
        e = edge_taken[curr]
        if e is not None:
            edges_in_path.append(e)
            crowds_in_path.append(edge_crowd_used.get(curr, e.crowd_score))
        curr = prev[curr]

    path.reverse()
    edges_in_path.reverse()
    crowds_in_path.reverse()

    # Aggregate component metrics along the chosen route
    total_dist = sum(e.distance for e in edges_in_path)
    total_time = sum(e.base_time for e in edges_in_path)
    num_edges = len(edges_in_path) if edges_in_path else 1

    avg_crowd = sum(crowds_in_path) / num_edges if crowds_in_path else 0.0
    avg_safety = sum(e.safety_score for e in edges_in_path) / num_edges
    avg_access = sum(e.accessibility_score for e in edges_in_path) / num_edges

    return MultiObjectiveResult(
        source_id=source_id,
        destination_id=destination_id,
        path=path,
        total_cost=round(g_cost[destination_id], 4),
        distance_m=round(total_dist, 2),
        travel_time_min=round(total_time, 4),
        crowd_score=round(avg_crowd, 4),
        crowd_level=crowd_score_to_level(avg_crowd),
        safety_score=round(avg_safety, 4),
        accessibility_score=round(avg_access, 4),
        execution_time_ms=round(elapsed_ms, 3),
        preference=preference,
        weights=weights.to_dict(),
        used_ml_crowd=used_ml_crowd,
        model_name=model_name if used_ml_crowd else None,
    )
