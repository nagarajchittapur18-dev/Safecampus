"""
SafeCampus AI — Phase 7 Automated Integration Tests
===================================================
Tests end-to-end integration:
Source → Destination → Preference → Graph → ML Crowd Prediction →
Edge Cost → Multi-Objective A* → Recommended Route

Verifies:
1. Loading trained ML model and integrating with routing cost function.
2. Dynamic replacement of static placeholder values with ML predictions.
3. Fallback behavior when ML is disabled or unavailable.
4. Validation of all required return attributes.
5. REST API endpoint POST /api/routes/recommend with ML crowd integration.
"""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.algorithms.multi_objective_a_star import WeightVector, multi_objective_a_star
from app.services.crowd_service import get_crowd_service
from app.services.graph_service import get_graph, reset_graph
from app.services.route_service import RouteService


# ---------------------------------------------------------------------------
# 1. Pipeline Integration Tests
# ---------------------------------------------------------------------------

class TestPhase7PipelineIntegration:
    def setup_method(self):
        reset_graph()
        self.graph = get_graph()
        self.route_service = RouteService()
        self.crowd_service = get_crowd_service()

    def test_ml_model_loaded_and_active(self):
        assert self.crowd_service.model is not None
        assert self.crowd_service.model_name == "GradientBoostingClassifier"

    def test_dynamic_ml_crowd_integrated_into_route(self):
        """
        Tests that recommend_route() invokes the ML model, converts predictions
        into normalized edge costs, and sets used_ml_crowd=True.
        """
        resp = self.route_service.recommend_route(
            source_id=1,
            destination_id=8,
            preference="balanced",
            hour=13,
            day_of_week=1,
            class_activity=1,
            use_ml_crowd=True,
        )

        assert resp.used_ml_crowd is True
        assert resp.model_name == "GradientBoostingClassifier"
        assert resp.route[0] == 1
        assert resp.route[-1] == 8
        assert resp.distance_m > 0.0
        assert resp.travel_time_min > 0.0
        assert 0.0 <= resp.crowd_score <= 1.0
        assert resp.crowd_level in ["LOW", "MEDIUM", "HIGH", "VERY_HIGH"]
        assert 0.0 <= resp.safety_score <= 1.0
        assert 0.0 <= resp.accessibility_score <= 1.0
        assert resp.total_cost > 0.0
        assert resp.execution_time_ms >= 0.0

    def test_temporal_context_changes_predicted_crowd_score(self):
        """
        Compares route crowd score during daytime rush (13:00, weekday)
        versus late night (23:00). Daytime rush should have higher crowd.
        """
        day_rush = self.route_service.recommend_route(
            source_id=1,
            destination_id=8,
            preference="shortest",
            hour=13,
            day_of_week=1,
            class_activity=1,
            use_ml_crowd=True,
        )

        night_quiet = self.route_service.recommend_route(
            source_id=1,
            destination_id=8,
            preference="shortest",
            hour=23,
            day_of_week=5,
            class_activity=0,
            use_ml_crowd=True,
        )

        assert day_rush.crowd_score > night_quiet.crowd_score, (
            f"Expected day rush crowd ({day_rush.crowd_score}) > night crowd ({night_quiet.crowd_score})"
        )

    def test_fallback_behavior_when_ml_disabled(self):
        """
        When use_ml_crowd=False, the routing algorithm must seamlessly fall back
        to static graph baselines, setting used_ml_crowd=False.
        """
        resp = self.route_service.recommend_route(
            source_id=1,
            destination_id=8,
            preference="balanced",
            use_ml_crowd=False,
        )

        assert resp.used_ml_crowd is False
        assert resp.model_name is None
        assert len(resp.route) >= 2
        assert resp.distance_m > 0.0
        assert resp.total_cost > 0.0

    def test_direct_algorithm_with_and_without_node_crowds(self):
        """
        Directly tests multi_objective_a_star with custom node_crowd_scores dict
        versus None (fallback).
        """
        custom_crowd = {n.id: 0.90 for n in self.graph.all_nodes()}
        r_ml = multi_objective_a_star(
            graph=self.graph,
            source_id=1,
            destination_id=4,
            preference="balanced",
            node_crowd_scores=custom_crowd,
            model_name="CustomMockModel",
        )
        assert r_ml.used_ml_crowd is True
        assert r_ml.model_name == "CustomMockModel"
        assert r_ml.crowd_score == pytest.approx(0.90, abs=1e-2)

        r_fallback = multi_objective_a_star(
            graph=self.graph,
            source_id=1,
            destination_id=4,
            preference="balanced",
            node_crowd_scores=None,
        )
        assert r_fallback.used_ml_crowd is False
        assert r_fallback.model_name is None


# ---------------------------------------------------------------------------
# 2. REST API Integration Tests: POST /api/routes/recommend
# ---------------------------------------------------------------------------

class TestPhase7APIIntegration:
    @pytest.fixture
    async def client(self):
        from app.main import app
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
            yield ac

    @pytest.mark.asyncio
    async def test_recommend_api_returns_all_required_attributes(self, client):
        resp = await client.post(
            "/api/routes/recommend",
            json={
                "source_id": 1,
                "destination_id": 8,
                "preference": "safest",
                "hour": 14,
                "day_of_week": 2,
                "class_activity": 1,
                "use_ml_crowd": True,
            },
        )
        assert resp.status_code == 200
        data = resp.json()

        # Requirement 7 verification:
        assert "route" in data
        assert "distance_m" in data
        assert "travel_time_min" in data
        assert "crowd_score" in data
        assert "crowd_level" in data
        assert "safety_score" in data
        assert "accessibility_score" in data
        assert "total_cost" in data
        assert "execution_time_ms" in data
        assert data["used_ml_crowd"] is True
        assert data["model_name"] == "GradientBoostingClassifier"

    @pytest.mark.asyncio
    async def test_recommend_api_fallback_mode(self, client):
        resp = await client.post(
            "/api/routes/recommend",
            json={
                "source_id": 1,
                "destination_id": 4,
                "preference": "shortest",
                "use_ml_crowd": False,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["used_ml_crowd"] is False
        assert data["model_name"] is None
        assert data["route"] == [1, 16, 17, 4]
