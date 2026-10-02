"""
SafeCampus AI — Unit Tests: Personalized Multi-Objective A*
============================================================
Tests the core research algorithm:
1. WeightVector validation (sum=1, non-negative, presets).
2. Edge cost calculation & factor normalization.
3. Multi-objective routing execution & component score calculation.
4. Preference sensitivity: demonstrating that varying weights produces different routes.
5. Equivalence to Dijkstra when distance weight wD=1.0.
6. Error handling (invalid nodes, disconnected targets, invalid weights).
7. REST API endpoint `POST /api/routes/recommend`.
"""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.algorithms.dijkstra import NodeNotFoundError, NoPathError, dijkstra
from app.algorithms.graph import CampusGraph
from app.algorithms.models import Edge, Node
from app.algorithms.multi_objective_a_star import (
    MultiObjectiveResult,
    WeightVector,
    calculate_edge_cost,
    crowd_score_to_level,
    multi_objective_a_star,
)
from app.services.graph_service import get_graph, reset_graph


# ---------------------------------------------------------------------------
# WeightVector Tests
# ---------------------------------------------------------------------------

class TestWeightVector:
    def test_valid_preset_creation(self):
        for preset in ["shortest", "fastest", "safest", "least_crowded", "accessible", "balanced"]:
            wv = WeightVector.from_preference(preset)
            assert isinstance(wv, WeightVector)
            total = wv.wD + wv.wT + wv.wC + wv.wS + wv.wA
            assert total == pytest.approx(1.0, abs=1e-4)

    def test_custom_valid_weights(self):
        wv = WeightVector(wD=0.4, wT=0.2, wC=0.2, wS=0.1, wA=0.1)
        assert wv.wD == 0.4
        assert wv.to_dict()["wD"] == 0.4

    def test_negative_weight_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            WeightVector(wD=-0.1, wT=0.3, wC=0.3, wS=0.3, wA=0.2)

    def test_sum_not_one_raises(self):
        with pytest.raises(ValueError, match="must sum to 1.0"):
            WeightVector(wD=0.5, wT=0.5, wC=0.5, wS=0.1, wA=0.1)

    def test_unknown_preference_preset_raises(self):
        with pytest.raises(ValueError, match="Unknown preference preset"):
            WeightVector.from_preference("invalid_preset")

    def test_case_insensitive_presets(self):
        wv1 = WeightVector.from_preference("SAFEST")
        wv2 = WeightVector.from_preference("safest")
        assert wv1 == wv2


# ---------------------------------------------------------------------------
# Normalization & Edge Cost Tests
# ---------------------------------------------------------------------------

class TestNormalizationAndCost:
    def test_edge_cost_in_unit_interval(self):
        reset_graph()
        g = get_graph()
        wv = WeightVector.from_preference("balanced")

        for edge in g.all_edges():
            cost = calculate_edge_cost(g, edge, wv)
            assert 0.0 <= cost <= 1.0, f"Edge cost {cost} outside [0, 1] for edge {edge.id}"

    def test_stairs_without_ramp_has_high_access_cost(self):
        reset_graph()
        g = get_graph()
        accessible_wv = WeightVector.from_preference("accessible")

        # Edge 8 has stairs and no ramp
        edge_with_stairs = g.get_edge(8)
        assert edge_with_stairs.stairs is True
        assert edge_with_stairs.ramp_available is False

        cost = calculate_edge_cost(g, edge_with_stairs, accessible_wv)
        # Accessibility factor is wA * 1.0 = 0.70
        assert cost >= 0.70

    def test_crowd_level_mapping(self):
        assert crowd_score_to_level(0.10) == "LOW"
        assert crowd_score_to_level(0.45) == "MEDIUM"
        assert crowd_score_to_level(0.70) == "HIGH"
        assert crowd_score_to_level(0.95) == "VERY_HIGH"


# ---------------------------------------------------------------------------
# Algorithm Core Tests
# ---------------------------------------------------------------------------

class TestMultiObjectiveAStarCore:
    def test_same_node_query(self):
        reset_graph()
        g = get_graph()
        r = multi_objective_a_star(g, 1, 1, preference="balanced")
        assert r.path == [1]
        assert r.total_cost == 0.0
        assert r.distance_m == 0.0
        assert r.travel_time_min == 0.0
        assert r.crowd_level == "LOW"

    def test_all_component_scores_populated(self):
        reset_graph()
        g = get_graph()
        r = multi_objective_a_star(g, 1, 8, preference="balanced")

        assert isinstance(r, MultiObjectiveResult)
        assert r.total_cost > 0.0
        assert r.distance_m > 0.0
        assert r.travel_time_min > 0.0
        assert 0.0 <= r.crowd_score <= 1.0
        assert r.crowd_level in ["LOW", "MEDIUM", "HIGH", "VERY_HIGH"]
        assert 0.0 <= r.safety_score <= 1.0
        assert 0.0 <= r.accessibility_score <= 1.0
        assert r.execution_time_ms >= 0.0
        assert r.path[0] == 1
        assert r.path[-1] == 8

    def test_unreachable_node_raises_no_path(self):
        reset_graph()
        g = get_graph()
        g.add_node(Node(id=999, name="Isolated Island", latitude=13.5, longitude=78.5, node_type="building"))
        with pytest.raises(NoPathError):
            multi_objective_a_star(g, 1, 999)

    def test_invalid_node_raises_not_found(self):
        reset_graph()
        g = get_graph()
        with pytest.raises(NodeNotFoundError):
            multi_objective_a_star(g, 9999, 1)


# ---------------------------------------------------------------------------
# CRITICAL: Route Differentiation across Preferences
# ---------------------------------------------------------------------------

class TestPreferenceRouteDifferentiation:
    """
    Verifies that changing the user preference and weight vector produces
    different recommended routes on the campus graph.
    """

    def test_route_change_node_1_to_node_4(self):
        """
        Main Gate (1) to CSE Block (4):
        - shortest: uses shortcut [1, 16, 17, 4] (270 m)
        - safest: uses safer avenue [1, 2, 3, 6, 4] (380 m, safety > 0.90)
        """
        reset_graph()
        g = get_graph()

        r_shortest = multi_objective_a_star(g, 1, 4, preference="shortest")
        r_safest = multi_objective_a_star(g, 1, 4, preference="safest")

        assert r_shortest.path != r_safest.path, (
            f"Expected different paths, but both chose: {r_shortest.path}"
        )
        assert r_shortest.distance_m < r_safest.distance_m
        assert r_safest.safety_score > r_shortest.safety_score

    def test_route_change_node_1_to_node_8(self):
        """
        Main Gate (1) to Canteen (8):
        - shortest: uses Corridor C bottleneck [1, 16, 17, 8] (300 m)
        - least_crowded: avoids crowded Corridor C via [1, 2, 3, 6, 4, 9, 8]
        """
        reset_graph()
        g = get_graph()

        r_shortest = multi_objective_a_star(g, 1, 8, preference="shortest")
        r_least_crowded = multi_objective_a_star(g, 1, 8, preference="least_crowded")

        assert r_shortest.path != r_least_crowded.path, (
            f"Expected different paths, but both chose: {r_shortest.path}"
        )
        assert r_least_crowded.crowd_score < r_shortest.crowd_score

    def test_route_change_node_1_to_node_11(self):
        """
        Main Gate (1) to Auditorium (11):
        - shortest: back route via [1, 16, 17, 4, 9, 10, 18, 11]
        - safest: main avenue via [1, 2, 3, 6, 7, 11]
        """
        reset_graph()
        g = get_graph()

        r_shortest = multi_objective_a_star(g, 1, 11, preference="shortest")
        r_safest = multi_objective_a_star(g, 1, 11, preference="safest")

        assert r_shortest.path != r_safest.path
        assert r_safest.safety_score > r_shortest.safety_score

    def test_route_change_node_1_to_node_13_accessible_avoids_stairs(self):
        """
        Main Gate (1) to Hostel A (13):
        - Auditorium to Hostel A (11->13) has stairs!
        - accessible preference detours via Hostel B (14) and Side Gate (20) which has ramps!
        """
        reset_graph()
        g = get_graph()

        r_safest = multi_objective_a_star(g, 1, 13, preference="safest")
        r_accessible = multi_objective_a_star(g, 1, 13, preference="accessible")

        assert r_accessible.path != r_safest.path
        # Edge 11->13 has stairs and no ramp, so accessible route must avoid it
        assert not (11 in r_accessible.path and 13 in r_accessible.path and
                    r_accessible.path.index(13) == r_accessible.path.index(11) + 1)


# ---------------------------------------------------------------------------
# Ablation: Pure Distance Weight (wD=1.0) matches Dijkstra
# ---------------------------------------------------------------------------

class TestAblationEquivalence:
    def test_pure_distance_matches_dijkstra(self):
        reset_graph()
        g = get_graph()

        pure_distance_wv = WeightVector(wD=1.0, wT=0.0, wC=0.0, wS=0.0, wA=0.0)

        for dst in [4, 8, 11, 13, 20]:
            r_dijkstra = dijkstra(g, 1, dst)
            r_moa = multi_objective_a_star(g, 1, dst, weights=pure_distance_wv)

            assert r_moa.distance_m == pytest.approx(r_dijkstra.distance_m), (
                f"For 1->{dst}: MOA distance {r_moa.distance_m} != Dijkstra {r_dijkstra.distance_m}"
            )


# ---------------------------------------------------------------------------
# API Tests: POST /api/routes/recommend
# ---------------------------------------------------------------------------

class TestRecommendRouteAPI:
    @pytest.fixture
    async def client(self):
        from app.main import app
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
            yield ac

    @pytest.mark.asyncio
    async def test_recommend_success_default_balanced(self, client):
        resp = await client.post(
            "/api/routes/recommend",
            json={"source_id": 1, "destination_id": 8},
        )
        assert resp.status_code == 200
        data = resp.json()

        assert data["preference"] == "balanced"
        assert "route" in data
        assert "recommended_route" in data
        assert "route_names" in data
        assert "distance_m" in data
        assert "travel_time_min" in data
        assert "crowd_score" in data
        assert "crowd_level" in data
        assert "safety_score" in data
        assert "accessibility_score" in data
        assert "total_cost" in data
        assert "execution_time_ms" in data
        assert data["algorithm"] == "personalized_multi_objective_a_star"

    @pytest.mark.asyncio
    async def test_recommend_safest_preference(self, client):
        resp = await client.post(
            "/api/routes/recommend",
            json={"source_id": 1, "destination_id": 4, "preference": "safest"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["preference"] == "safest"
        assert data["route"] == [1, 2, 3, 6, 4]
        assert data["safety_score"] > 0.88

    @pytest.mark.asyncio
    async def test_recommend_custom_weights(self, client):
        resp = await client.post(
            "/api/routes/recommend",
            json={
                "source_id": 1,
                "destination_id": 8,
                "weights": {
                    "wD": 0.5,
                    "wT": 0.2,
                    "wC": 0.1,
                    "wS": 0.1,
                    "wA": 0.1,
                },
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["weights"]["wD"] == 0.5

    @pytest.mark.asyncio
    async def test_recommend_invalid_weights_sum(self, client):
        resp = await client.post(
            "/api/routes/recommend",
            json={
                "source_id": 1,
                "destination_id": 8,
                "weights": {
                    "wD": 0.9,
                    "wT": 0.9,
                    "wC": 0.1,
                    "wS": 0.1,
                    "wA": 0.1,
                },
            },
        )
        assert resp.status_code == 422
        assert "detail" in resp.json()

    @pytest.mark.asyncio
    async def test_recommend_invalid_preference_string(self, client):
        resp = await client.post(
            "/api/routes/recommend",
            json={"source_id": 1, "destination_id": 8, "preference": "teleportation"},
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_recommend_not_found_node(self, client):
        resp = await client.post(
            "/api/routes/recommend",
            json={"source_id": 9999, "destination_id": 8},
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_recommend_returns_alternatives(self, client):
        resp = await client.post(
            "/api/routes/recommend",
            json={"source_id": 1, "destination_id": 8, "preference": "balanced"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "alternatives" in data
        assert isinstance(data["alternatives"], list)
        for alt in data["alternatives"]:
            assert "label" in alt
            assert "preference" in alt
            assert "route" in alt
            assert len(alt["route"]) >= 2
            assert "distance_m" in alt
            assert "travel_time_min" in alt
            assert "safety_score" in alt
            assert "crowd_score" in alt
            assert "accessibility_score" in alt

