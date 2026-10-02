"""
SafeCampus AI — A* Shortest-Path Routing Algorithm
===================================================
Finds the minimum-distance path between two nodes in a CampusGraph using
heuristic-guided A* search.

Heuristic
---------
Uses straight-line geographic (Haversine) distance from the current node to the
destination node:
    h(u) = u.distance_to(destination)

Admissibility & Consistency:
* The great-circle / Haversine distance is the shortest possible surface distance
  between two coordinates.
* Campus paths are constrained by walkways, corridors, and roads, so physical
  walking distance >= straight-line distance.
* Therefore, h(u) <= true_distance(u, dest), making h(u) admissible.
* By the triangle inequality of the Haversine metric on a sphere,
  h(u) <= dist(u, v) + h(v), making h(u) consistent (monotonic).
* Consistency guarantees that the first time a node is expanded, the optimal
  path to it has been found.

Execution Time
--------------
Execution time is measured with high precision using `time.perf_counter()` and
reported in milliseconds (ms).
"""

from __future__ import annotations

import heapq
import math
import time
from dataclasses import dataclass
from typing import Dict, List, Optional

from app.algorithms.dijkstra import NodeNotFoundError, NoPathError
from app.algorithms.graph import CampusGraph


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AStarResult:
    """Immutable result returned by the a_star() function."""

    source_id: int
    destination_id: int
    path: List[int]             # Ordered list of node IDs (source → … → dest)
    distance_m: float           # Total path distance in metres
    travel_time_min: float      # Sum of edge base_time values in minutes
    execution_time_ms: float    # Algorithm execution duration in milliseconds

    @property
    def reachable(self) -> bool:
        return len(self.path) > 0

    def __str__(self) -> str:
        if not self.reachable:
            return (
                f"AStarResult: no path from {self.source_id} "
                f"to {self.destination_id}"
            )
        return (
            f"AStarResult: {' → '.join(str(n) for n in self.path)} | "
            f"{self.distance_m:.1f} m | {self.travel_time_min:.2f} min | "
            f"{self.execution_time_ms:.3f} ms"
        )


# ---------------------------------------------------------------------------
# Algorithm
# ---------------------------------------------------------------------------

def a_star(
    graph: CampusGraph,
    source_id: int,
    destination_id: int,
) -> AStarResult:
    """
    Run A* shortest-path algorithm on *graph* from *source_id* to *destination_id*.

    Parameters
    ----------
    graph          : Loaded CampusGraph instance.
    source_id      : Start node ID.
    destination_id : Target node ID.

    Returns
    -------
    AStarResult with path, distance_m, travel_time_min, and execution_time_ms.

    Raises
    ------
    NodeNotFoundError : if source_id or destination_id is not in graph.
    NoPathError       : if destination is unreachable.
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

    # ---- Same source and destination ----
    if source_id == destination_id:
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return AStarResult(
            source_id=source_id,
            destination_id=destination_id,
            path=[source_id],
            distance_m=0.0,
            travel_time_min=0.0,
            execution_time_ms=round(elapsed_ms, 3),
        )

    dest_node = graph.get_node(destination_id)
    assert dest_node is not None

    # ---- Initialise structures ----
    # g_score[u] = exact known shortest distance from source to u
    g_score: Dict[int, float] = {n.id: math.inf for n in graph.all_nodes()}
    g_score[source_id] = 0.0

    # time_accum[u] = cumulative travel time from source to u
    time_accum: Dict[int, float] = {n.id: 0.0 for n in graph.all_nodes()}

    # prev[u] = previous node on the shortest path
    prev: Dict[int, Optional[int]] = {n.id: None for n in graph.all_nodes()}

    # Heuristic for start node
    start_node = graph.get_node(source_id)
    assert start_node is not None
    h_start = start_node.distance_to(dest_node)

    # Priority queue stores tuples: (f_score, tie_breaker, node_id)
    entry_count = 0
    open_set: List[tuple] = [(h_start, entry_count, source_id)]
    closed_set: set[int] = set()

    found = False

    # ---- Search loop ----
    while open_set:
        current_f, _, u = heapq.heappop(open_set)

        if u in closed_set:
            continue
        closed_set.add(u)

        if u == destination_id:
            found = True
            break

        current_g = g_score[u]

        for edge in graph.neighbors(u):
            v = edge.destination
            if v in closed_set:
                continue

            tentative_g = current_g + edge.distance

            if tentative_g < g_score[v]:
                g_score[v] = tentative_g
                time_accum[v] = time_accum[u] + edge.base_time
                prev[v] = u

                v_node = graph.get_node(v)
                assert v_node is not None
                h_v = v_node.distance_to(dest_node)
                f_v = tentative_g + h_v

                entry_count += 1
                heapq.heappush(open_set, (f_v, entry_count, v))

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    if not found or math.isinf(g_score[destination_id]):
        raise NoPathError(
            f"No path from node {source_id} to node {destination_id} "
            f"in the campus graph."
        )

    # ---- Reconstruct path ----
    path: List[int] = []
    curr: Optional[int] = destination_id
    while curr is not None:
        path.append(curr)
        curr = prev[curr]
    path.reverse()

    return AStarResult(
        source_id=source_id,
        destination_id=destination_id,
        path=path,
        distance_m=round(g_score[destination_id], 2),
        travel_time_min=round(time_accum[destination_id], 4),
        execution_time_ms=round(elapsed_ms, 3),
    )
