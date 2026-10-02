"""
SafeCampus AI — Unit Tests: Locations API
GET /api/locations
GET /api/locations/{id}
"""

import json
import pytest
from pathlib import Path
from httpx import ASGITransport, AsyncClient


@pytest.fixture
async def client():
    from app.main import app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


# ---------------------------------------------------------------------------
# GET /api/locations
# ---------------------------------------------------------------------------

class TestListLocations:
    @pytest.mark.asyncio
    async def test_returns_200(self, client):
        response = await client.get("/api/locations")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_returns_count_field(self, client):
        response = await client.get("/api/locations")
        data = response.json()
        assert "count" in data
        assert data["count"] == 20  # 20 nodes in campus_nodes.json

    @pytest.mark.asyncio
    async def test_returns_locations_list(self, client):
        response = await client.get("/api/locations")
        data = response.json()
        assert "locations" in data
        assert isinstance(data["locations"], list)
        assert len(data["locations"]) == 20

    @pytest.mark.asyncio
    async def test_location_has_required_fields(self, client):
        response = await client.get("/api/locations")
        loc = response.json()["locations"][0]
        for field in ("id", "name", "latitude", "longitude", "location_type"):
            assert field in loc, f"Missing field: {field}"

    @pytest.mark.asyncio
    async def test_location_coordinates_are_floats(self, client):
        response = await client.get("/api/locations")
        loc = response.json()["locations"][0]
        assert isinstance(loc["latitude"], float)
        assert isinstance(loc["longitude"], float)

    @pytest.mark.asyncio
    async def test_main_gate_is_present(self, client):
        response = await client.get("/api/locations")
        names = [l["name"] for l in response.json()["locations"]]
        assert "Main Gate" in names

    @pytest.mark.asyncio
    async def test_locations_sorted_by_id(self, client):
        response = await client.get("/api/locations")
        ids = [l["id"] for l in response.json()["locations"]]
        assert ids == sorted(ids)


# ---------------------------------------------------------------------------
# GET /api/locations/{id}
# ---------------------------------------------------------------------------

class TestGetLocation:
    @pytest.mark.asyncio
    async def test_returns_200_for_valid_id(self, client):
        response = await client.get("/api/locations/1")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_returns_correct_location(self, client):
        response = await client.get("/api/locations/1")
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "Main Gate"
        assert data["location_type"] == "gate"

    @pytest.mark.asyncio
    async def test_returns_404_for_unknown_id(self, client):
        response = await client.get("/api/locations/9999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_404_has_detail_field(self, client):
        response = await client.get("/api/locations/9999")
        assert "detail" in response.json()

    @pytest.mark.asyncio
    async def test_library_location(self, client):
        response = await client.get("/api/locations/7")
        data = response.json()
        assert data["name"] == "Library"
        assert data["location_type"] == "library"

    @pytest.mark.asyncio
    async def test_all_node_ids_reachable(self, client):
        for node_id in range(1, 21):
            response = await client.get(f"/api/locations/{node_id}")
            assert response.status_code == 200, f"Node {node_id} returned {response.status_code}"
