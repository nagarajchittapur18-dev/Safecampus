"""
SafeCampus AI — Unit Tests: Route Recommendation Explanation Engine (Phase 11)
================================================================================
Verifies:
1. Dynamic explanations for why the route was selected.
2. Exact calculation of distance, time, crowd, safety, and accessibility trade-offs.
3. Actual differences against Dijkstra shortest path baseline (never hard-coded).
4. Prompt example fulfillment:
   "Recommended because predicted crowd is low and the route has a high safety score."
5. POST /api/routes/explain and POST /api/routes/recommend explanation payloads.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.algorithms.dijkstra import dijkstra
from app.algorithms.multi_objective_a_star import (
    WeightVector,
    multi_objective_a_star,
)
from app.services.explanation_service import (
    ExplanationEngine,
    evaluate_path_metrics,
    get_explanation_engine,
)
from app.services.graph_service import get_graph, reset_graph


@pytest.fixture(autouse=True)
def setup_campus_graph():
    reset_graph()
    return get_graph()


@pytest.fixture
async def client():
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


class TestExplanationEngineUnit:
    """Unit tests for ExplanationEngine logic and metric calculations."""

    def test_evaluate_path_metrics_valid_path(self, setup_campus_graph):
        g = setup_campus_graph
        path = [1, 2, 3]
        metrics = evaluate_path_metrics(g, path)

        assert metrics["distance_m"] > 0
        assert metrics["travel_time_min"] > 0
        assert 0.0 <= metrics["safety_score"] <= 1.0
        assert 0.0 <= metrics["accessibility_score"] <= 1.0
        assert len(metrics["edges"]) == 2

    def test_evaluate_path_metrics_single_node(self, setup_campus_graph):
        g = setup_campus_graph
        metrics = evaluate_path_metrics(g, [1])
        assert metrics["distance_m"] == 0.0
        assert metrics["travel_time_min"] == 0.0
        assert metrics["crowd_score"] == 0.0
        assert metrics["safety_score"] == 1.0

    def test_shortest_preference_has_zero_distance_tradeoff(self, setup_campus_graph):
        g = setup_campus_graph
        engine = get_explanation_engine()

        # For 'shortest', recommended path is identical to Dijkstra shortest path
        res = multi_objective_a_star(g, 1, 8, preference="shortest")
        explanation = engine.generate_explanation(g, res, 1, 8)

        tradeoffs = explanation.tradeoffs
        assert tradeoffs["distance"]["difference"] == pytest.approx(0.0, abs=1e-2)
        assert tradeoffs["distance"]["percentage_difference"] == pytest.approx(0.0, abs=1e-1)
        assert "0m detour" in explanation.distance_tradeoff or "shortest" in explanation.distance_tradeoff.lower()

    def test_safest_preference_calculates_actual_differences(self, setup_campus_graph):
        g = setup_campus_graph
        engine = get_explanation_engine()

        # From node 1 to node 11, safest detours via Main Avenue to avoid dim alleys
        res = multi_objective_a_star(g, 1, 11, preference="safest")
        explanation = engine.generate_explanation(g, res, 1, 11)

        dijkstra_res = dijkstra(g, 1, 11)
        expected_diff_dist = round(res.distance_m - dijkstra_res.distance_m, 2)

        tradeoffs = explanation.tradeoffs
        assert tradeoffs["distance"]["difference"] == pytest.approx(expected_diff_dist, abs=1e-2)
        assert tradeoffs["safety"]["recommended"] == pytest.approx(res.safety_score, abs=1e-2)
        assert tradeoffs["safety"]["difference"] >= 0.0

        # Verify dynamic string contains the actual measured difference (never hard-coded)
        assert str(int(round(abs(expected_diff_dist)))) in explanation.distance_tradeoff
        assert "safety" in explanation.safety_tradeoff.lower()

    def test_least_crowded_generates_example_rationale(self, setup_campus_graph):
        """
        Tests the user prompt requirement:
        'Recommended because predicted crowd is low and the route has a high safety score.'
        """
        g = setup_campus_graph
        engine = get_explanation_engine()

        # Controlled low crowd scores
        node_crowd = {nid: 0.15 for nid in [1, 2, 3, 6, 4, 9, 8]}
        res = multi_objective_a_star(
            g, 1, 8, preference="least_crowded", node_crowd_scores=node_crowd
        )
        explanation = engine.generate_explanation(
            g, res, 1, 8, node_crowd_scores=node_crowd
        )

        assert res.crowd_score <= 0.35
        assert res.safety_score >= 0.80
        # Check that the summary fulfills the example phrasing:
        assert (
            explanation.summary
            == "Recommended because predicted crowd is low and the route has a high safety score."
        )

    def test_accessible_explains_ramp_and_stair_tradeoff(self, setup_campus_graph):
        g = setup_campus_graph
        engine = get_explanation_engine()

        # 1 to 13: Dijkstra uses 11->13 which has stairs. Accessible preference avoids it.
        res = multi_objective_a_star(g, 1, 13, preference="accessible")
        explanation = engine.generate_explanation(g, res, 1, 13)

        assert "accessible" in explanation.why_selected.lower() or "accessibility" in explanation.accessibility_tradeoff.lower()
        assert explanation.tradeoffs["accessibility"]["recommended"] >= explanation.tradeoffs["accessibility"]["shortest"]
        assert len(explanation.reasons) >= 3

    def test_never_hardcoded_values_match_actual_metrics(self, setup_campus_graph):
        """Verify that numerical text in narratives reflects actual computed numbers."""
        g = setup_campus_graph
        engine = get_explanation_engine()

        res = multi_objective_a_star(g, 1, 4, preference="safest")
        explanation = engine.generate_explanation(g, res, 1, 4)

        t = explanation.tradeoffs
        diff_dist = t["distance"]["difference"]
        diff_time = t["travel_time"]["difference"]

        # Ensure the formatted numbers inside the string match the calculated floats
        if diff_dist > 0:
            assert f"{int(round(diff_dist))}m" in explanation.distance_tradeoff
        if abs(diff_time) > 0.05:
            assert f"{abs(diff_time):.1f} min" in explanation.time_tradeoff


class TestExplanationAPI:
    """Integration tests for POST /api/routes/explain and Recommend Route API."""

    @pytest.mark.asyncio
    async def test_recommend_includes_explanation(self, client):
        resp = await client.post(
            "/api/routes/recommend",
            json={"source_id": 1, "destination_id": 8, "preference": "balanced"},
        )
        assert resp.status_code == 200
        data = resp.json()

        assert "explanation" in data
        assert data["explanation"] is not None
        exp = data["explanation"]

        assert "summary" in exp
        assert "why_selected" in exp
        assert "distance_tradeoff" in exp
        assert "time_tradeoff" in exp
        assert "crowd_tradeoff" in exp
        assert "safety_tradeoff" in exp
        assert "accessibility_tradeoff" in exp
        assert "tradeoffs" in exp
        assert "shortest_baseline" in exp
        assert len(exp["reasons"]) > 0

    @pytest.mark.asyncio
    async def test_explain_endpoint_success(self, client):
        resp = await client.post(
            "/api/routes/explain",
            json={"source_id": 1, "destination_id": 11, "preference": "safest"},
        )
        assert resp.status_code == 200
        data = resp.json()

        assert data["source_id"] == 1
        assert data["destination_id"] == 11
        assert data["preference"] == "safest"
        assert "explanation" in data
        assert "recommendation" in data

        exp = data["explanation"]
        assert "safest" in exp["why_selected"].lower() or "safety" in exp["summary"].lower()
        assert exp["shortest_baseline"]["distance_m"] > 0
        assert exp["tradeoffs"]["safety"]["recommended"] > 0.8

    @pytest.mark.asyncio
    async def test_explain_endpoint_invalid_node_returns_404(self, client):
        resp = await client.post(
            "/api/routes/explain",
            json={"source_id": 9999, "destination_id": 1},
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_explain_endpoint_invalid_weights_returns_422(self, client):
        resp = await client.post(
            "/api/routes/explain",
            json={
                "source_id": 1,
                "destination_id": 8,
                "weights": {"wD": 0.9, "wT": 0.9, "wC": 0.1, "wS": 0.1, "wA": 0.1},
            },
        )
        assert resp.status_code == 422
