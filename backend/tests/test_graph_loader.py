"""
SafeCampus AI — Unit Tests: Graph Loader (graph_service.py)
"""

import json
import tempfile
from pathlib import Path

import pytest

from app.services.graph_service import load_graph, reset_graph


# ---------------------------------------------------------------------------
# Fixtures — write minimal JSON files to a temp dir
# ---------------------------------------------------------------------------

NODES_DATA = [
    {"id": 1, "name": "Gate",    "latitude": 12.97, "longitude": 77.59, "type": "gate"},
    {"id": 2, "name": "Library", "latitude": 12.98, "longitude": 77.60, "type": "library"},
    {"id": 3, "name": "Canteen", "latitude": 12.99, "longitude": 77.61, "type": "canteen"},
]

EDGES_DATA = [
    {
        "id": 1, "source": 1, "destination": 2,
        "distance": 150.0, "base_time": 2.0,
        "safety_score": 0.85, "accessibility_score": 0.90,
        "stairs": False, "ramp_available": True,
    },
    {
        "id": 2, "source": 2, "destination": 3,
        "distance": 100.0, "base_time": 1.5,
        "safety_score": 0.80, "accessibility_score": 0.85,
        "stairs": False, "ramp_available": True,
    },
]


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset the graph singleton before and after each test."""
    reset_graph()
    yield
    reset_graph()


@pytest.fixture
def tmp_data_dir(tmp_path):
    nodes_file = tmp_path / "campus_nodes.json"
    edges_file = tmp_path / "campus_edges.json"
    nodes_file.write_text(json.dumps(NODES_DATA), encoding="utf-8")
    edges_file.write_text(json.dumps(EDGES_DATA), encoding="utf-8")
    return tmp_path


# ---------------------------------------------------------------------------
# Loader tests
# ---------------------------------------------------------------------------

class TestGraphLoader:
    def test_loads_correct_node_count(self, tmp_data_dir):
        g = load_graph(
            nodes_path=tmp_data_dir / "campus_nodes.json",
            edges_path=tmp_data_dir / "campus_edges.json",
        )
        assert g.node_count() == 3

    def test_loads_correct_edge_count(self, tmp_data_dir):
        g = load_graph(
            nodes_path=tmp_data_dir / "campus_nodes.json",
            edges_path=tmp_data_dir / "campus_edges.json",
        )
        assert g.edge_count() == 2

    def test_bidirectional_creates_reverse_neighbors(self, tmp_data_dir):
        g = load_graph(
            nodes_path=tmp_data_dir / "campus_nodes.json",
            edges_path=tmp_data_dir / "campus_edges.json",
            bidirectional=True,
        )
        # Node 2 should have neighbors both 1 (reversed edge) and 3 (original)
        dests = {e.destination for e in g.neighbors(2)}
        assert 1 in dests
        assert 3 in dests

    def test_directed_only_no_reverse(self, tmp_data_dir):
        g = load_graph(
            nodes_path=tmp_data_dir / "campus_nodes.json",
            edges_path=tmp_data_dir / "campus_edges.json",
            bidirectional=False,
        )
        # Node 2 is only a destination in edge 1→2; it has no outgoing edge to 1
        dests = {e.destination for e in g.neighbors(2)}
        assert 1 not in dests  # no reverse
        assert 3 in dests      # edge 2→3 exists

    def test_node_data_preserved(self, tmp_data_dir):
        g = load_graph(
            nodes_path=tmp_data_dir / "campus_nodes.json",
            edges_path=tmp_data_dir / "campus_edges.json",
        )
        node = g.get_node(1)
        assert node.name == "Gate"
        assert node.node_type == "gate"
        assert node.latitude == pytest.approx(12.97)

    def test_edge_data_preserved(self, tmp_data_dir):
        g = load_graph(
            nodes_path=tmp_data_dir / "campus_nodes.json",
            edges_path=tmp_data_dir / "campus_edges.json",
        )
        edges = g.neighbors(1)
        assert len(edges) == 1
        e = edges[0]
        assert e.distance == pytest.approx(150.0)
        assert e.safety_score == pytest.approx(0.85)
        assert e.ramp_available is True

    def test_missing_nodes_file_raises(self, tmp_path):
        edges_file = tmp_path / "campus_edges.json"
        edges_file.write_text(json.dumps(EDGES_DATA), encoding="utf-8")
        with pytest.raises(FileNotFoundError):
            load_graph(
                nodes_path=tmp_path / "missing_nodes.json",
                edges_path=edges_file,
            )

    def test_missing_edges_file_raises(self, tmp_path):
        nodes_file = tmp_path / "campus_nodes.json"
        nodes_file.write_text(json.dumps(NODES_DATA), encoding="utf-8")
        with pytest.raises(FileNotFoundError):
            load_graph(
                nodes_path=nodes_file,
                edges_path=tmp_path / "missing_edges.json",
            )

    def test_invalid_edge_reference_raises(self, tmp_path):
        nodes_file = tmp_path / "campus_nodes.json"
        edges_file = tmp_path / "campus_edges.json"
        nodes_file.write_text(json.dumps(NODES_DATA), encoding="utf-8")
        bad_edges = [
            {
                "id": 99, "source": 1, "destination": 999,  # node 999 doesn't exist
                "distance": 100, "base_time": 1.5,
                "safety_score": 0.8, "accessibility_score": 0.9,
                "stairs": False, "ramp_available": True,
            }
        ]
        edges_file.write_text(json.dumps(bad_edges), encoding="utf-8")
        with pytest.raises(ValueError, match="unknown nodes"):
            load_graph(nodes_path=nodes_file, edges_path=edges_file)

    def test_node_missing_required_field_raises(self, tmp_path):
        nodes_file = tmp_path / "campus_nodes.json"
        edges_file = tmp_path / "campus_edges.json"
        bad_nodes = [{"id": 1, "name": "Gate"}]  # missing lat/lon/type
        nodes_file.write_text(json.dumps(bad_nodes), encoding="utf-8")
        edges_file.write_text(json.dumps([]), encoding="utf-8")
        with pytest.raises(ValueError, match="missing fields"):
            load_graph(nodes_path=nodes_file, edges_path=edges_file)

    def test_loads_real_campus_data(self):
        """Integration test: loads actual campus_nodes.json + campus_edges.json."""
        g = load_graph()
        assert g.node_count() == 20
        assert g.edge_count() == 35
        errors = g.validate()
        assert errors == [], f"Graph validation errors: {errors}"
