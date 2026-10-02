"""
SafeCampus AI — Unit Tests: POST /api/routes/dijkstra
"""

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
async def client():
    from app.main import app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


# ---------------------------------------------------------------------------
# Successful responses
# ---------------------------------------------------------------------------

class TestDijkstraAPI:
    @pytest.mark.asyncio
    async def test_returns_200(self, client):
        response = await client.post(
            "/api/routes/dijkstra",
            json={"source_id": 1, "destination_id": 8},
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_response_has_required_fields(self, client):
        response = await client.post(
            "/api/routes/dijkstra",
            json={"source_id": 1, "destination_id": 8},
        )
        data = response.json()
        for field in ("route", "route_names", "distance_m", "travel_time_min", "algorithm"):
            assert field in data, f"Missing field: {field}"

    @pytest.mark.asyncio
    async def test_route_starts_at_source(self, client):
        response = await client.post(
            "/api/routes/dijkstra",
            json={"source_id": 1, "destination_id": 8},
        )
        data = response.json()
        assert data["route"][0] == 1

    @pytest.mark.asyncio
    async def test_route_ends_at_destination(self, client):
        response = await client.post(
            "/api/routes/dijkstra",
            json={"source_id": 1, "destination_id": 8},
        )
        data = response.json()
        assert data["route"][-1] == 8

    @pytest.mark.asyncio
    async def test_distance_is_positive_float(self, client):
        response = await client.post(
            "/api/routes/dijkstra",
            json={"source_id": 1, "destination_id": 8},
        )
        data = response.json()
        assert isinstance(data["distance_m"], (int, float))
        assert data["distance_m"] > 0

    @pytest.mark.asyncio
    async def test_travel_time_is_positive_float(self, client):
        response = await client.post(
            "/api/routes/dijkstra",
            json={"source_id": 1, "destination_id": 8},
        )
        data = response.json()
        assert isinstance(data["travel_time_min"], (int, float))
        assert data["travel_time_min"] > 0

    @pytest.mark.asyncio
    async def test_route_names_match_route_length(self, client):
        response = await client.post(
            "/api/routes/dijkstra",
            json={"source_id": 1, "destination_id": 8},
        )
        data = response.json()
        assert len(data["route_names"]) == len(data["route"])

    @pytest.mark.asyncio
    async def test_algorithm_field_is_dijkstra(self, client):
        response = await client.post(
            "/api/routes/dijkstra",
            json={"source_id": 1, "destination_id": 8},
        )
        assert response.json()["algorithm"] == "dijkstra"

    @pytest.mark.asyncio
    async def test_source_equals_destination_returns_single_node(self, client):
        response = await client.post(
            "/api/routes/dijkstra",
            json={"source_id": 3, "destination_id": 3},
        )
        data = response.json()
        assert response.status_code == 200
        assert data["route"] == [3]
        assert data["distance_m"] == 0.0
        assert data["travel_time_min"] == 0.0

    @pytest.mark.asyncio
    async def test_first_route_name_is_main_gate(self, client):
        response = await client.post(
            "/api/routes/dijkstra",
            json={"source_id": 1, "destination_id": 8},
        )
        data = response.json()
        assert data["route_names"][0] == "Main Gate"

    @pytest.mark.asyncio
    async def test_last_route_name_is_canteen(self, client):
        response = await client.post(
            "/api/routes/dijkstra",
            json={"source_id": 1, "destination_id": 8},
        )
        data = response.json()
        assert data["route_names"][-1] == "Canteen"


# ---------------------------------------------------------------------------
# Error responses
# ---------------------------------------------------------------------------

class TestDijkstraAPIErrors:
    @pytest.mark.asyncio
    async def test_unknown_source_returns_404(self, client):
        response = await client.post(
            "/api/routes/dijkstra",
            json={"source_id": 9999, "destination_id": 8},
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_unknown_destination_returns_404(self, client):
        response = await client.post(
            "/api/routes/dijkstra",
            json={"source_id": 1, "destination_id": 9999},
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_404_response_has_detail(self, client):
        response = await client.post(
            "/api/routes/dijkstra",
            json={"source_id": 9999, "destination_id": 8},
        )
        assert "detail" in response.json()

    @pytest.mark.asyncio
    async def test_missing_source_id_returns_422(self, client):
        response = await client.post(
            "/api/routes/dijkstra",
            json={"destination_id": 8},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_missing_destination_id_returns_422(self, client):
        response = await client.post(
            "/api/routes/dijkstra",
            json={"source_id": 1},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_negative_source_id_returns_422(self, client):
        response = await client.post(
            "/api/routes/dijkstra",
            json={"source_id": -1, "destination_id": 8},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_empty_body_returns_422(self, client):
        response = await client.post("/api/routes/dijkstra", json={})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_string_ids_return_422(self, client):
        response = await client.post(
            "/api/routes/dijkstra",
            json={"source_id": "gate", "destination_id": "library"},
        )
        assert response.status_code == 422
