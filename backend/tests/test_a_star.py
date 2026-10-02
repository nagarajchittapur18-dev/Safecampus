"""
SafeCampus AI — Unit Tests: A* Shortest-Path Algorithm
======================================================
Tests A* algorithm on:
1. The hand-verified 6-node graph.
2. The full 20-node campus graph.
3. Comparative optimality tests against Dijkstra.
4. Heuristic validation (admissibility & consistency).
5. Error handling (unreachable nodes, missing nodes).
6. Execution time measurement.
7. REST API endpoint `POST /api/routes/a-star`.
"""

from __future__ import annotations

import math
import pytest
from httpx import ASGITransport, AsyncClient

from app.algorithms.a_star import AStarResult, a_star
from app.algorithms.dijkstra import (
    NodeNotFoundError,
    NoPathError,
    dijkstra,
)
from app.algorithms.graph import CampusGraph
from app.algorithms.models import Edge, Node, haversine_metres
from app.services.graph_service import get_graph, reset_graph


# ---------------------------------------------------------------------------
# Fixture: Known 6-Node Graph
# ---------------------------------------------------------------------------

def make_node(nid: int, lat_offset: float = 0.0, lon_offset: float = 0.0) -> Node:
    return Node(
        id=nid,
        name=f"Node{nid}",
        latitude=12.9710 + lat_offset,
        longitude=77.5940 + lon_offset,
        node_type="junction",
    )


def make_edge(eid: int, src: int, dst: int, dist: float, time: float) -> Edge:
    return Edge(
        id=eid,
        source=src,
        destination=dst,
        distance=dist,
        base_time=time,
        safety_score=0.85,
        accessibility_score=0.90,
        stairs=False,
        ramp_available=True,
    )


@pytest.fixture
def known_graph() -> CampusGraph:
    """
    Hand-verifiable 6-node graph:
    1 --100-- 2 --80-- 3
    |                  |
    150                60
    |                  |
    4 -------200------ 5 --110-- 6
    """
    g = CampusGraph()
    # Coordinates placed such that straight-line distances are <= edge distances
    g.add_node(make_node(1, lat_offset=0.0000, lon_offset=0.0000))
    g.add_node(make_node(2, lat_offset=0.0005, lon_offset=0.0005))
    g.add_node(make_node(3, lat_offset=0.0008, lon_offset=0.0010))
    g.add_node(make_node(4, lat_offset=-0.0008, lon_offset=0.0000))
    g.add_node(make_node(5, lat_offset=0.0002, lon_offset=0.0012))
    g.add_node(make_node(6, lat_offset=0.0002, lon_offset=0.0020))

    g.add_edge(make_edge(1, 1, 2, 100, 1.5), bidirectional=True)
    g.add_edge(make_edge(2, 2, 3,  80, 1.2), bidirectional=True)
    g.add_edge(make_edge(3, 3, 5,  60, 0.9), bidirectional=True)
    g.add_edge(make_edge(4, 1, 4, 150, 2.2), bidirectional=True)
    g.add_edge(make_edge(5, 4, 5, 200, 3.0), bidirectional=True)
    g.add_edge(make_edge(6, 5, 6, 110, 1.7), bidirectional=True)
    return g


# ---------------------------------------------------------------------------
# Heuristic Validation Tests
# ---------------------------------------------------------------------------

class TestAStarHeuristic:
    def test_heuristic_zero_at_goal(self, known_graph):
        """h(goal, goal) must be exactly 0."""
        goal = known_graph.get_node(5)
        assert goal.distance_to(goal) == pytest.approx(0.0)

    def test_heuristic_admissibility_on_campus_graph(self):
        """
        Admissibility: For every node u and destination dest,
        h(u, dest) <= shortest_path_distance(u, dest).
        Tested on the actual campus graph using Dijkstra as ground truth.
        """
        reset_graph()
        g = get_graph()
        dest_id = 8  # Canteen
        dest_node = g.get_node(dest_id)

        for u in g.all_nodes():
            if u.id == dest_id:
                continue
            h_val = u.distance_to(dest_node)
            dijkstra_res = dijkstra(g, u.id, dest_id)
            assert h_val <= dijkstra_res.distance_m + 1e-5, (
                f"Heuristic inadmissible for node {u.id}: h={h_val} > true={dijkstra_res.distance_m}"
            )

    def test_heuristic_consistency_triangle_inequality(self):
        """
        Consistency: For every directed edge (u, v),
        h(u, goal) <= edge.distance + h(v, goal).
        """
        reset_graph()
        g = get_graph()
        goal = g.get_node(11)  # Auditorium

        for edge in g.all_edges():
            u_node = g.get_node(edge.source)
            v_node = g.get_node(edge.destination)

            h_u = u_node.distance_to(goal)
            h_v = v_node.distance_to(goal)

            assert h_u <= edge.distance + h_v + 1e-5, (
                f"Heuristic inconsistent on edge {edge.source}->{edge.destination}: "
                f"h(u)={h_u} > dist={edge.distance} + h(v)={h_v}"
            )


# ---------------------------------------------------------------------------
# Algorithm Correctness & Format Tests
# ---------------------------------------------------------------------------

class TestAStarCorrectness:
    def test_two_hop_path(self, known_graph):
        r = a_star(known_graph, 1, 3)
        assert isinstance(r, AStarResult)
        assert r.path == [1, 2, 3]
        assert r.distance_m == pytest.approx(180.0)
        assert r.travel_time_min == pytest.approx(2.7, rel=1e-3)
        assert r.execution_time_ms >= 0.0

    def test_three_hop_path(self, known_graph):
        r = a_star(known_graph, 1, 5)
        # Optimal path: 1->2->3->5 = 240 m (vs 1->4->5 = 350 m)
        assert r.path == [1, 2, 3, 5]
        assert r.distance_m == pytest.approx(240.0)

    def test_same_node_query(self, known_graph):
        r = a_star(known_graph, 2, 2)
        assert r.path == [2]
        assert r.distance_m == 0.0
        assert r.travel_time_min == 0.0
        assert r.execution_time_ms >= 0.0

    def test_execution_time_measured(self, known_graph):
        r = a_star(known_graph, 1, 6)
        assert isinstance(r.execution_time_ms, float)
        assert r.execution_time_ms >= 0.0

    def test_str_representation(self, known_graph):
        r = a_star(known_graph, 1, 3)
        s = str(r)
        assert "1 → 2 → 3" in s
        assert "180.0 m" in s
        assert "ms" in s


# ---------------------------------------------------------------------------
# Test Against Dijkstra (Comparative Benchmark)
# ---------------------------------------------------------------------------

class TestAStarVersusDijkstra:
    @pytest.mark.parametrize("src,dst", [
        (1, 2),
        (1, 3),
        (1, 4),
        (1, 5),
        (1, 6),
        (4, 3),
        (6, 1),
    ])
    def test_known_graph_identical_distance_to_dijkstra(self, known_graph, src, dst):
        r_dijkstra = dijkstra(known_graph, src, dst)
        r_astar = a_star(known_graph, src, dst)

        assert r_astar.distance_m == pytest.approx(r_dijkstra.distance_m), (
            f"Distance mismatch between A* ({r_astar.distance_m}) and Dijkstra ({r_dijkstra.distance_m})"
        )
        assert r_astar.travel_time_min == pytest.approx(r_dijkstra.travel_time_min, rel=1e-3)

    @pytest.mark.parametrize("src,dst", [
        (1, 8),    # Main Gate to Canteen
        (1, 11),   # Main Gate to Auditorium
        (1, 20),   # Main Gate to Side Gate
        (16, 14),  # Parking Lot to Hostel B
        (15, 10),  # Health Center to Lab B
        (2, 13),   # Admin Block to Hostel A
    ])
    def test_campus_graph_identical_distance_to_dijkstra(self, src, dst):
        reset_graph()
        g = get_graph()

        r_dijkstra = dijkstra(g, src, dst)
        r_astar = a_star(g, src, dst)

        assert r_astar.distance_m == pytest.approx(r_dijkstra.distance_m), (
            f"Distance mismatch for {src}->{dst}: A*={r_astar.distance_m}, Dijkstra={r_dijkstra.distance_m}"
        )
        assert r_astar.travel_time_min == pytest.approx(r_dijkstra.travel_time_min, rel=1e-3)
        assert r_astar.path[0] == src
        assert r_astar.path[-1] == dst


# ---------------------------------------------------------------------------
# Error Handling
# ---------------------------------------------------------------------------

class TestAStarErrors:
    def test_invalid_source_raises_node_not_found(self, known_graph):
        with pytest.raises(NodeNotFoundError, match="Source node"):
            a_star(known_graph, 9999, 1)

    def test_invalid_destination_raises_node_not_found(self, known_graph):
        with pytest.raises(NodeNotFoundError, match="Destination node"):
            a_star(known_graph, 1, 9999)

    def test_unreachable_node_raises_no_path(self, known_graph):
        known_graph.add_node(make_node(99, lat_offset=0.01, lon_offset=0.01))
        with pytest.raises(NoPathError, match="No path"):
            a_star(known_graph, 1, 99)


# ---------------------------------------------------------------------------
# API Tests: POST /api/routes/a-star
# ---------------------------------------------------------------------------

class TestAStarAPI:
    @pytest.fixture
    async def client(self):
        from app.main import app
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
            yield ac

    @pytest.mark.asyncio
    async def test_a_star_api_success(self, client):
        resp = await client.post(
            "/api/routes/a-star",
            json={"source_id": 1, "destination_id": 8},
        )
        assert resp.status_code == 200
        data = resp.json()

        assert "route" in data
        assert "distance_m" in data
        assert "travel_time_min" in data
        assert "execution_time_ms" in data
        assert "route_names" in data
        assert data["algorithm"] == "a_star"

        assert data["route"][0] == 1
        assert data["route"][-1] == 8
        assert data["distance_m"] > 0
        assert data["travel_time_min"] > 0
        assert data["execution_time_ms"] >= 0.0

    @pytest.mark.asyncio
    async def test_a_star_api_same_node(self, client):
        resp = await client.post(
            "/api/routes/a-star",
            json={"source_id": 5, "destination_id": 5},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["route"] == [5]
        assert data["distance_m"] == 0.0
        assert data["travel_time_min"] == 0.0

    @pytest.mark.asyncio
    async def test_a_star_api_not_found(self, client):
        resp = await client.post(
            "/api/routes/a-star",
            json={"source_id": 9999, "destination_id": 1},
        )
        assert resp.status_code == 404
        assert "detail" in resp.json()

    @pytest.mark.asyncio
    async def test_a_star_api_validation_error(self, client):
        resp = await client.post(
            "/api/routes/a-star",
            json={"source_id": -1, "destination_id": 8},
        )
        assert resp.status_code == 422
