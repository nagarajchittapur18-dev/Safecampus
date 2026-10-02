"""
SafeCampus AI — Unit Tests: CampusGraph
"""

import pytest

from app.algorithms.graph import CampusGraph
from app.algorithms.models import Edge, Node


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_node(id: int, lat: float = 12.97, lon: float = 77.59) -> Node:
    return Node(id=id, name=f"Node{id}", latitude=lat, longitude=lon, node_type="junction")


def make_edge(id: int, src: int, dst: int, dist: float = 100.0) -> Edge:
    return Edge(
        id=id, source=src, destination=dst,
        distance=dist, base_time=1.5,
        safety_score=0.8, accessibility_score=0.9,
        stairs=False, ramp_available=True,
    )


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------

class TestGraphConstruction:
    def test_empty_graph(self):
        g = CampusGraph()
        assert g.node_count() == 0
        assert g.edge_count() == 0

    def test_add_single_node(self):
        g = CampusGraph()
        g.add_node(make_node(1))
        assert g.node_count() == 1
        assert g.has_node(1)

    def test_add_duplicate_node_raises(self):
        g = CampusGraph()
        g.add_node(make_node(1))
        with pytest.raises(ValueError, match="Duplicate node"):
            g.add_node(make_node(1))

    def test_add_edge_without_nodes_raises(self):
        g = CampusGraph()
        with pytest.raises(ValueError, match="unknown nodes"):
            g.add_edge(make_edge(1, 1, 2), bidirectional=False)

    def test_add_edge_missing_source_raises(self):
        g = CampusGraph()
        g.add_node(make_node(2))  # only destination exists
        with pytest.raises(ValueError, match="source=1"):
            g.add_edge(make_edge(1, 1, 2), bidirectional=False)

    def test_add_edge_missing_destination_raises(self):
        g = CampusGraph()
        g.add_node(make_node(1))  # only source exists
        with pytest.raises(ValueError, match="destination=2"):
            g.add_edge(make_edge(1, 1, 2), bidirectional=False)

    def test_add_directed_edge(self):
        g = CampusGraph()
        g.add_node(make_node(1))
        g.add_node(make_node(2))
        g.add_edge(make_edge(1, 1, 2), bidirectional=False)
        # 1 original + 0 reversed
        assert g.edge_count() == 1
        assert len(g.neighbors(1)) == 1
        assert len(g.neighbors(2)) == 0  # directed only

    def test_add_bidirectional_edge(self):
        g = CampusGraph()
        g.add_node(make_node(1))
        g.add_node(make_node(2))
        g.add_edge(make_edge(1, 1, 2), bidirectional=True)
        assert g.edge_count() == 1          # only original counted
        assert len(g.neighbors(1)) == 1     # 1→2
        assert len(g.neighbors(2)) == 1     # 2→1 (reversed)


# ---------------------------------------------------------------------------
# Accessors
# ---------------------------------------------------------------------------

class TestGraphAccessors:
    def setup_method(self):
        self.g = CampusGraph()
        self.g.add_node(make_node(1, lat=12.97, lon=77.59))
        self.g.add_node(make_node(2, lat=12.98, lon=77.60))
        self.g.add_node(make_node(3, lat=12.99, lon=77.61))
        self.g.add_edge(make_edge(1, 1, 2, dist=150), bidirectional=True)
        self.g.add_edge(make_edge(2, 2, 3, dist=200), bidirectional=True)

    def test_get_existing_node(self):
        node = self.g.get_node(1)
        assert node is not None
        assert node.id == 1

    def test_get_nonexistent_node_returns_none(self):
        assert self.g.get_node(999) is None

    def test_all_nodes_count(self):
        assert len(self.g.all_nodes()) == 3

    def test_all_edges_count(self):
        assert self.g.edge_count() == 2

    def test_neighbors_of_node_1(self):
        neighbors = self.g.neighbors(1)
        assert len(neighbors) == 1
        assert neighbors[0].destination == 2

    def test_neighbors_of_node_2_bidirectional(self):
        # Node 2 is connected to both 1 and 3 via bidirectional edges
        neighbors = self.g.neighbors(2)
        dests = {e.destination for e in neighbors}
        assert 1 in dests
        assert 3 in dests

    def test_neighbors_nonexistent_node(self):
        assert self.g.neighbors(999) == []


# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------

class TestNormalization:
    def setup_method(self):
        self.g = CampusGraph()
        self.g.add_node(make_node(1))
        self.g.add_node(make_node(2))
        self.g.add_edge(make_edge(1, 1, 2, dist=200.0), bidirectional=False)

    def test_normalize_distance_max(self):
        # Normalizing the max distance should give 1.0
        val = self.g.normalize_distance(200.0)
        assert val == pytest.approx(1.0)

    def test_normalize_distance_half(self):
        val = self.g.normalize_distance(100.0)
        assert val == pytest.approx(0.5)

    def test_normalize_distance_zero(self):
        val = self.g.normalize_distance(0.0)
        assert val == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# Graph validation
# ---------------------------------------------------------------------------

class TestGraphValidation:
    def test_empty_graph_has_errors(self):
        g = CampusGraph()
        errors = g.validate()
        assert any("no nodes" in e.lower() for e in errors)

    def test_valid_graph_no_errors(self):
        g = CampusGraph()
        g.add_node(make_node(1))
        g.add_node(make_node(2))
        g.add_edge(make_edge(1, 1, 2), bidirectional=True)
        errors = g.validate()
        assert errors == []

    def test_isolated_node_reported(self):
        g = CampusGraph()
        g.add_node(make_node(1))
        g.add_node(make_node(2))  # node 2 isolated — no edges
        g.add_node(make_node(3))
        g.add_edge(make_edge(1, 1, 3), bidirectional=True)
        errors = g.validate()
        assert any("Isolated" in e for e in errors)

    def test_repr_contains_counts(self):
        g = CampusGraph()
        g.add_node(make_node(1))
        g.add_node(make_node(2))
        g.add_edge(make_edge(1, 1, 2), bidirectional=True)
        r = repr(g)
        assert "nodes=2" in r
        assert "edges=1" in r
