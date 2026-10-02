"""
SafeCampus AI — Dijkstra's Shortest-Path Algorithm
===================================================
Finds the minimum-distance path between two nodes in a CampusGraph.

Design notes
------------
* Uses a min-heap (heapq) for O((V + E) log V) performance.
* Edge weight = edge.distance (metres).
* Returns a DijkstraResult dataclass — never raw dicts — so callers get
  typed, validated data.
* All values computed from real graph data; nothing is fabricated.

Usage
-----
    from app.algorithms.dijkstra import dijkstra, DijkstraResult

    result = dijkstra(graph, source_id=1, destination_id=8)
    # result.path           → [1, 3, 6, 8]        (ordered node IDs)
    # result.distance_m     → 425.0                (total metres)
    # result.travel_time_min → 5.3                 (sum of edge base_time)
"""

from __future__ import annotations

import heapq
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from app.algorithms.graph import CampusGraph


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class DijkstraResult:
    """Immutable result returned by the dijkstra() function."""

    source_id: int
    destination_id: int
    path: List[int]             # Ordered list of node IDs (source → … → dest)
    distance_m: float           # Total path distance in metres
    travel_time_min: float      # Sum of edge base_time values in minutes

    @property
    def reachable(self) -> bool:
        return len(self.path) > 0

    def __str__(self) -> str:
        if not self.reachable:
            return (
                f"DijkstraResult: no path from {self.source_id} "
                f"to {self.destination_id}"
            )
        return (
            f"DijkstraResult: {' → '.join(str(n) for n in self.path)} | "
            f"{self.distance_m:.1f} m | {self.travel_time_min:.2f} min"
        )


# ---------------------------------------------------------------------------
# Algorithm
# ---------------------------------------------------------------------------

class NodeNotFoundError(ValueError):
    """Raised when source or destination node ID is not in the graph."""


class NoPathError(ValueError):
    """Raised when no path exists between source and destination."""


def dijkstra(
    graph: CampusGraph,
    source_id: int,
    destination_id: int,
) -> DijkstraResult:
    """
    Run Dijkstra's algorithm on *graph* from *source_id* to *destination_id*.

    The edge weight is ``edge.distance`` (metres).
    Travel time is accumulated from ``edge.base_time`` along the chosen path.

    Parameters
    ----------
    graph          : Loaded CampusGraph instance.
    source_id      : ID of the start node.
    destination_id : ID of the target node.

    Returns
    -------
    DijkstraResult with path, distance_m, and travel_time_min.

    Raises
    ------
    NodeNotFoundError : if source_id or destination_id is not in the graph.
    NoPathError       : if destination is unreachable from source.
    """
    # ---- Input validation ----
    _validate_nodes(graph, source_id, destination_id)

    # ---- Same source and destination ----
    if source_id == destination_id:
        return DijkstraResult(
            source_id=source_id,
            destination_id=destination_id,
            path=[source_id],
            distance_m=0.0,
            travel_time_min=0.0,
        )

    # ---- Initialise data structures ----
    # dist[node_id] = best known distance from source
    dist: Dict[int, float] = {
        n.id: math.inf for n in graph.all_nodes()
    }
    dist[source_id] = 0.0

    # time[node_id] = cumulative base_time along best path
    time_accum: Dict[int, float] = {
        n.id: 0.0 for n in graph.all_nodes()
    }

    # prev[node_id] = predecessor node on best path
    prev: Dict[int, Optional[int]] = {n.id: None for n in graph.all_nodes()}

    # Min-heap: (distance, node_id)
    heap: List[tuple] = [(0.0, source_id)]

    visited: set = set()

    # ---- Relaxation loop ----
    while heap:
        current_dist, u = heapq.heappop(heap)

        if u in visited:
            continue
        visited.add(u)

        if u == destination_id:
            break  # optimal path found

        for edge in graph.neighbors(u):
            v = edge.destination
            if v in visited:
                continue

            new_dist = current_dist + edge.distance
            if new_dist < dist[v]:
                dist[v] = new_dist
                time_accum[v] = time_accum[u] + edge.base_time
                prev[v] = u
                heapq.heappush(heap, (new_dist, v))

    # ---- Check reachability ----
    if math.isinf(dist[destination_id]):
        raise NoPathError(
            f"No path from node {source_id} to node {destination_id} "
            f"in the campus graph."
        )

    # ---- Reconstruct path ----
    path = _reconstruct_path(prev, source_id, destination_id)

    return DijkstraResult(
        source_id=source_id,
        destination_id=destination_id,
        path=path,
        distance_m=round(dist[destination_id], 2),
        travel_time_min=round(time_accum[destination_id], 4),
    )


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _validate_nodes(
    graph: CampusGraph, source_id: int, destination_id: int
) -> None:
    errors = []
    if not graph.has_node(source_id):
        errors.append(f"Source node {source_id!r} not found in campus graph.")
    if not graph.has_node(destination_id):
        errors.append(f"Destination node {destination_id!r} not found in campus graph.")
    if errors:
        raise NodeNotFoundError(" | ".join(errors))


def _reconstruct_path(
    prev: Dict[int, Optional[int]],
    source_id: int,
    destination_id: int,
) -> List[int]:
    """Walk backwards through the prev map to build the ordered path."""
    path: List[int] = []
    current: Optional[int] = destination_id

    while current is not None:
        path.append(current)
        current = prev[current]

    path.reverse()

    # Sanity check: path must start at source
    if path[0] != source_id:
        return []

    return path
