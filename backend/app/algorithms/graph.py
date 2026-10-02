"""
SafeCampus AI — Campus Graph Data Structure
============================================
In-memory adjacency-list graph built from campus_nodes.json
and campus_edges.json.

All routing algorithms operate on CampusGraph.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Optional

from app.algorithms.models import Edge, Node


class CampusGraph:
    """
    Directed weighted graph of campus locations.

    Internally uses an adjacency list:
        _adj[node_id] → List[Edge]   (outgoing edges)

    Bidirectionality is handled at load time: when the loader calls
    add_edge(edge, bidirectional=True), the reversed edge is inserted
    automatically.
    """

    def __init__(self) -> None:
        self._nodes: Dict[int, Node] = {}
        self._edges: Dict[int, Edge] = {}          # edge_id → Edge
        self._adj: Dict[int, List[Edge]] = defaultdict(list)

        # Pre-computed stats for normalization (populated in _compute_stats)
        self._max_distance: float = 1.0
        self._max_time: float = 1.0

    # ------------------------------------------------------------------
    # Building the graph
    # ------------------------------------------------------------------

    def add_node(self, node: Node) -> None:
        """Add a node. Raises ValueError if the ID already exists."""
        if node.id in self._nodes:
            raise ValueError(f"Duplicate node ID: {node.id}")
        self._nodes[node.id] = node

    def add_edge(self, edge: Edge, bidirectional: bool = True) -> None:
        """
        Add a directed edge (source → destination).
        If bidirectional=True, also add the reversed edge.

        Raises:
            ValueError: if source/destination node IDs are not in the graph.
        """
        self._validate_edge_nodes(edge)

        self._edges[edge.id] = edge
        self._adj[edge.source].append(edge)

        if bidirectional:
            rev = edge.reversed()
            self._edges[rev.id] = rev
            self._adj[rev.source].append(rev)

        self._compute_stats()

    def _validate_edge_nodes(self, edge: Edge) -> None:
        missing = []
        if edge.source not in self._nodes:
            missing.append(f"source={edge.source}")
        if edge.destination not in self._nodes:
            missing.append(f"destination={edge.destination}")
        if missing:
            raise ValueError(
                f"Edge {edge.id} references unknown nodes: {', '.join(missing)}"
            )

    def _compute_stats(self) -> None:
        """Recompute normalisation stats after each edge addition."""
        distances = [e.distance for e in self._edges.values()]
        times = [e.base_time for e in self._edges.values()]
        self._max_distance = max(distances) if distances else 1.0
        self._max_time = max(times) if times else 1.0

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    def get_node(self, node_id: int) -> Optional[Node]:
        return self._nodes.get(node_id)

    def get_edge(self, edge_id: int) -> Optional[Edge]:
        return self._edges.get(edge_id)

    def neighbors(self, node_id: int) -> List[Edge]:
        """Return all outgoing edges from node_id."""
        return self._adj.get(node_id, [])

    def all_nodes(self) -> List[Node]:
        return list(self._nodes.values())

    def all_edges(self) -> List[Edge]:
        """Return only the original (non-reversed) edges."""
        return [e for e in self._edges.values() if e.id > 0]

    def has_node(self, node_id: int) -> bool:
        return node_id in self._nodes

    def node_count(self) -> int:
        return len(self._nodes)

    def edge_count(self) -> int:
        """Count of original edges (not reversed copies)."""
        return sum(1 for eid in self._edges if eid > 0)

    # ------------------------------------------------------------------
    # Normalization helpers (used by multi-objective cost function)
    # ------------------------------------------------------------------

    def normalize_distance(self, distance: float) -> float:
        return distance / self._max_distance if self._max_distance > 0 else 0.0

    def normalize_time(self, time: float) -> float:
        return time / self._max_time if self._max_time > 0 else 0.0

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(self) -> List[str]:
        """
        Run consistency checks on the graph.
        Returns a list of error strings (empty list = valid).
        """
        errors: List[str] = []

        if self.node_count() == 0:
            errors.append("Graph has no nodes.")

        if self.edge_count() == 0:
            errors.append("Graph has no edges.")

        # Check all edge references
        for edge in self._edges.values():
            if edge.source not in self._nodes:
                errors.append(f"Edge {edge.id}: source {edge.source} not in nodes.")
            if edge.destination not in self._nodes:
                errors.append(f"Edge {edge.id}: dest {edge.destination} not in nodes.")

        # Check for isolated nodes
        connected = set()
        for edge in self._edges.values():
            connected.add(edge.source)
            connected.add(edge.destination)
        isolated = [n.id for n in self._nodes.values() if n.id not in connected]
        if isolated:
            errors.append(f"Isolated nodes (no edges): {isolated}")

        return errors

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"<CampusGraph nodes={self.node_count()} "
            f"edges={self.edge_count()}>"
        )
