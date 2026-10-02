"""
SafeCampus AI — Unit Tests: Graph Data Models (Node, Edge, Haversine)
"""

import math
import pytest

from app.algorithms.models import Edge, Node, haversine_metres


# ---------------------------------------------------------------------------
# Node tests
# ---------------------------------------------------------------------------

class TestNode:
    def test_node_creation(self):
        node = Node(id=1, name="Main Gate", latitude=12.97, longitude=77.59,
                    node_type="gate", description="Primary entrance")
        assert node.id == 1
        assert node.name == "Main Gate"
        assert node.node_type == "gate"

    def test_node_is_frozen(self):
        node = Node(id=1, name="Main Gate", latitude=12.97, longitude=77.59,
                    node_type="gate")
        with pytest.raises((AttributeError, TypeError)):
            node.id = 99  # type: ignore[misc]

    def test_node_distance_to_self_is_zero(self):
        node = Node(id=1, name="A", latitude=12.97, longitude=77.59, node_type="gate")
        assert node.distance_to(node) == pytest.approx(0.0, abs=1e-6)

    def test_node_distance_to_other_positive(self):
        a = Node(id=1, name="A", latitude=12.9716, longitude=77.5946, node_type="gate")
        b = Node(id=2, name="B", latitude=12.9720, longitude=77.5950, node_type="building")
        dist = a.distance_to(b)
        assert dist > 0
        # Two nodes ~50 m apart should return a value in that ballpark
        assert 30 < dist < 100

    def test_node_str(self):
        node = Node(id=5, name="Library", latitude=12.97, longitude=77.59,
                    node_type="library")
        assert "5" in str(node)
        assert "Library" in str(node)


# ---------------------------------------------------------------------------
# Edge tests
# ---------------------------------------------------------------------------

class TestEdge:
    def _make_edge(self, **overrides):
        defaults = dict(
            id=1, source=1, destination=2,
            distance=100.0, base_time=1.5,
            safety_score=0.85, accessibility_score=0.90,
            stairs=False, ramp_available=True,
        )
        defaults.update(overrides)
        return Edge(**defaults)

    def test_edge_creation(self):
        edge = self._make_edge()
        assert edge.source == 1
        assert edge.destination == 2
        assert edge.distance == 100.0
        assert edge.safety_score == 0.85

    def test_edge_invalid_safety_score_high(self):
        with pytest.raises(ValueError, match="safety_score"):
            self._make_edge(safety_score=1.5)

    def test_edge_invalid_safety_score_low(self):
        with pytest.raises(ValueError, match="safety_score"):
            self._make_edge(safety_score=-0.1)

    def test_edge_invalid_accessibility_score(self):
        with pytest.raises(ValueError, match="accessibility_score"):
            self._make_edge(accessibility_score=2.0)

    def test_edge_invalid_distance(self):
        with pytest.raises(ValueError, match="distance"):
            self._make_edge(distance=0)

    def test_edge_invalid_base_time(self):
        with pytest.raises(ValueError, match="base_time"):
            self._make_edge(base_time=-1.0)

    def test_edge_reversed(self):
        edge = self._make_edge(id=7, source=3, destination=5)
        rev = edge.reversed()
        assert rev.source == 5
        assert rev.destination == 3
        assert rev.id == -7
        assert rev.distance == edge.distance
        assert rev.safety_score == edge.safety_score

    def test_edge_reversed_twice_restores_direction(self):
        edge = self._make_edge(id=7, source=3, destination=5)
        double_rev = edge.reversed().reversed()
        assert double_rev.source == edge.source
        assert double_rev.destination == edge.destination

    def test_edge_str(self):
        edge = self._make_edge(id=1, source=1, destination=2)
        s = str(edge)
        assert "1→2" in s


# ---------------------------------------------------------------------------
# Haversine tests
# ---------------------------------------------------------------------------

class TestHaversine:
    def test_same_point_is_zero(self):
        assert haversine_metres(12.97, 77.59, 12.97, 77.59) == pytest.approx(0.0, abs=1e-6)

    def test_known_distance(self):
        # Bengaluru city centre → ~1 km north
        d = haversine_metres(12.9716, 77.5946, 12.9806, 77.5946)
        assert 990 < d < 1010  # ~1 000 m

    def test_symmetry(self):
        d1 = haversine_metres(12.97, 77.59, 12.98, 77.60)
        d2 = haversine_metres(12.98, 77.60, 12.97, 77.59)
        assert d1 == pytest.approx(d2, rel=1e-9)

    def test_positive(self):
        d = haversine_metres(12.97, 77.59, 12.98, 77.60)
        assert d > 0
