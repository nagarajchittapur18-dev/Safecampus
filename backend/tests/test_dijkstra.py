"""
SafeCampus AI — Unit Tests: Dijkstra Algorithm
================================================
Tests use a small, fully hand-verifiable graph so every expected value
can be confirmed without running the algorithm mentally.

Graph topology (all edges bidirectional):

    A(1) ──100── B(2) ──80──  C(3)
      |                        |
     150                      60
      |                        |
    D(4) ──────200────────── E(5)
                               |
                              110
                               |
                             F(6)

Edge distances (metres) and base_time (minutes):

  1→2 : dist=100, time=1.5
  2→3 : dist=80,  time=1.2
  3→5 : dist=60,  time=0.9
  1→4 : dist=150, time=2.2
  4→5 : dist=200, time=3.0
  5→6 : dist=110, time=1.7

Shortest-path facts (verified by hand):
  1 → 3 : path [1,2,3]    dist=180   time=2.7
  1 → 5 : path [1,2,3,5]  dist=240   time=3.6
  1 → 6 : path [1,2,3,5,6] dist=350  time=5.3
  1 → 4 : path [1,4]      dist=150   time=2.2
  1 → 1 : path [1]        dist=0     time=0
"""

from __future__ import annotations

import pytest

from app.algorithms.dijkstra import (
    DijkstraResult,
    NodeNotFoundError,
    NoPathError,
    dijkstra,
)
from app.algorithms.graph import CampusGraph
from app.algorithms.models import Edge, Node


# ---------------------------------------------------------------------------
# Known-graph fixture
# ---------------------------------------------------------------------------

def make_node(nid: int) -> Node:
    return Node(id=nid, name=f"Node{nid}", latitude=12.97 + nid * 0.001,
                longitude=77.59 + nid * 0.001, node_type="junction")


def make_edge(eid, src, dst, dist, time) -> Edge:
    return Edge(
        id=eid, source=src, destination=dst,
        distance=dist, base_time=time,
        safety_score=0.85, accessibility_score=0.90,
        stairs=False, ramp_available=True,
    )


@pytest.fixture
def known_graph() -> CampusGraph:
    """
    Build the hand-verifiable 6-node graph described in the module docstring.
    All edges are bidirectional.
    """
    g = CampusGraph()
    for i in range(1, 7):
        g.add_node(make_node(i))

    g.add_edge(make_edge(1, 1, 2, 100, 1.5), bidirectional=True)  # A–B
    g.add_edge(make_edge(2, 2, 3,  80, 1.2), bidirectional=True)  # B–C
    g.add_edge(make_edge(3, 3, 5,  60, 0.9), bidirectional=True)  # C–E
    g.add_edge(make_edge(4, 1, 4, 150, 2.2), bidirectional=True)  # A–D
    g.add_edge(make_edge(5, 4, 5, 200, 3.0), bidirectional=True)  # D–E
    g.add_edge(make_edge(6, 5, 6, 110, 1.7), bidirectional=True)  # E–F
    return g


# ---------------------------------------------------------------------------
# DijkstraResult dataclass tests
# ---------------------------------------------------------------------------

class TestDijkstraResult:
    def test_reachable_when_path_exists(self):
        r = DijkstraResult(
            source_id=1, destination_id=3,
            path=[1, 2, 3], distance_m=180.0, travel_time_min=2.7,
        )
        assert r.reachable is True

    def test_not_reachable_when_path_empty(self):
        r = DijkstraResult(
            source_id=1, destination_id=3,
            path=[], distance_m=0.0, travel_time_min=0.0,
        )
        assert r.reachable is False

    def test_str_contains_path(self):
        r = DijkstraResult(
            source_id=1, destination_id=3,
            path=[1, 2, 3], distance_m=180.0, travel_time_min=2.7,
        )
        assert "1 → 2 → 3" in str(r)

    def test_str_no_path(self):
        r = DijkstraResult(
            source_id=1, destination_id=3,
            path=[], distance_m=0.0, travel_time_min=0.0,
        )
        assert "no path" in str(r)


# ---------------------------------------------------------------------------
# Core correctness tests
# ---------------------------------------------------------------------------

class TestDijkstraCorrectness:
    def test_simple_two_hop_path(self, known_graph):
        r = dijkstra(known_graph, 1, 3)
        assert r.path == [1, 2, 3]
        assert r.distance_m == pytest.approx(180.0)
        assert r.travel_time_min == pytest.approx(2.7, rel=1e-3)

    def test_three_hop_path(self, known_graph):
        r = dijkstra(known_graph, 1, 5)
        # Shortest: 1→2→3→5 = 100+80+60 = 240
        # Alternative: 1→4→5 = 150+200 = 350 (longer)
        assert r.path == [1, 2, 3, 5]
        assert r.distance_m == pytest.approx(240.0)

    def test_four_hop_path(self, known_graph):
        r = dijkstra(known_graph, 1, 6)
        assert r.path == [1, 2, 3, 5, 6]
        assert r.distance_m == pytest.approx(350.0)
        assert r.travel_time_min == pytest.approx(5.3, rel=1e-3)

    def test_direct_edge_path(self, known_graph):
        r = dijkstra(known_graph, 1, 4)
        assert r.path == [1, 4]
        assert r.distance_m == pytest.approx(150.0)
        assert r.travel_time_min == pytest.approx(2.2)

    def test_reverse_direction_bidirectional(self, known_graph):
        r = dijkstra(known_graph, 6, 1)
        assert r.path[0] == 6
        assert r.path[-1] == 1
        assert r.distance_m == pytest.approx(350.0)

    def test_source_equals_destination(self, known_graph):
        r = dijkstra(known_graph, 3, 3)
        assert r.path == [3]
        assert r.distance_m == pytest.approx(0.0)
        assert r.travel_time_min == pytest.approx(0.0)

    def test_path_starts_at_source(self, known_graph):
        r = dijkstra(known_graph, 1, 6)
        assert r.path[0] == 1

    def test_path_ends_at_destination(self, known_graph):
        r = dijkstra(known_graph, 1, 6)
        assert r.path[-1] == 6

    def test_distance_is_positive(self, known_graph):
        r = dijkstra(known_graph, 2, 5)
        assert r.distance_m > 0

    def test_travel_time_is_positive(self, known_graph):
        r = dijkstra(known_graph, 2, 5)
        assert r.travel_time_min > 0

    def test_all_nodes_in_path_exist_in_graph(self, known_graph):
        r = dijkstra(known_graph, 1, 6)
        for nid in r.path:
            assert known_graph.has_node(nid)

    def test_consecutive_nodes_are_connected(self, known_graph):
        """Every consecutive pair in the path must be connected by an edge."""
        r = dijkstra(known_graph, 1, 6)
        for i in range(len(r.path) - 1):
            u, v = r.path[i], r.path[i + 1]
            neighbor_ids = {e.destination for e in known_graph.neighbors(u)}
            assert v in neighbor_ids, f"No edge from {u} to {v} in path"


# ---------------------------------------------------------------------------
# Optimality tests
# ---------------------------------------------------------------------------

class TestDijkstraOptimality:
    def test_dijkstra_prefers_shorter_path_over_fewer_hops(self, known_graph):
        """
        1→5: shorter path is 1→2→3→5 (240m, 3 hops)
             longer path is  1→4→5   (350m, 2 hops)
        Dijkstra must prefer the 240m path.
        """
        r = dijkstra(known_graph, 1, 5)
        assert r.distance_m == pytest.approx(240.0), (
            "Dijkstra chose the longer path (350m) over the shorter (240m)"
        )
        assert 2 in r.path, "Optimal path must go through node 2"

    def test_symmetric_distances(self, known_graph):
        """Forward and reverse paths should have the same total distance."""
        fwd = dijkstra(known_graph, 1, 6)
        rev = dijkstra(known_graph, 6, 1)
        assert fwd.distance_m == pytest.approx(rev.distance_m)


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

class TestDijkstraErrors:
    def test_invalid_source_raises_node_not_found(self, known_graph):
        with pytest.raises(NodeNotFoundError, match="Source node"):
            dijkstra(known_graph, 999, 3)

    def test_invalid_destination_raises_node_not_found(self, known_graph):
        with pytest.raises(NodeNotFoundError, match="Destination node"):
            dijkstra(known_graph, 1, 999)

    def test_both_invalid_raises_node_not_found(self, known_graph):
        with pytest.raises(NodeNotFoundError):
            dijkstra(known_graph, 888, 999)

    def test_unreachable_destination_raises_no_path(self, known_graph):
        """Add an isolated node 7 (no edges) and try to route to it."""
        known_graph.add_node(
            Node(id=7, name="Isolated", latitude=13.0, longitude=78.0,
                 node_type="junction")
        )
        with pytest.raises(NoPathError, match="No path"):
            dijkstra(known_graph, 1, 7)

    def test_directed_only_graph_blocks_reverse(self):
        """In a directed-only graph, routing against edge direction fails."""
        g = CampusGraph()
        g.add_node(make_node(1))
        g.add_node(make_node(2))
        g.add_edge(make_edge(1, 1, 2, 100, 1.5), bidirectional=False)

        # Forward works
        r = dijkstra(g, 1, 2)
        assert r.path == [1, 2]

        # Reverse has no path
        with pytest.raises(NoPathError):
            dijkstra(g, 2, 1)


# ---------------------------------------------------------------------------
# Integration test: real campus graph
# ---------------------------------------------------------------------------

class TestDijkstraIntegration:
    def test_main_gate_to_canteen_returns_valid_path(self):
        """Route on the real 20-node campus graph — values from actual data."""
        from app.services.graph_service import get_graph, reset_graph
        reset_graph()
        graph = get_graph()

        # Node 1 = Main Gate, Node 8 = Canteen
        r = dijkstra(graph, 1, 8)

        assert r.path[0] == 1
        assert r.path[-1] == 8
        assert r.distance_m > 0
        assert r.travel_time_min > 0
        assert len(r.path) >= 2

    def test_all_nodes_reachable_from_main_gate(self):
        """Every node in the real campus graph should be reachable from node 1."""
        from app.services.graph_service import get_graph, reset_graph
        reset_graph()
        graph = get_graph()

        unreachable = []
        for node in graph.all_nodes():
            if node.id == 1:
                continue
            try:
                dijkstra(graph, 1, node.id)
            except NoPathError:
                unreachable.append(node.id)

        assert unreachable == [], (
            f"These nodes are unreachable from Main Gate (node 1): {unreachable}"
        )
