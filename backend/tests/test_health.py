"""
SafeCampus AI — Backend Test Suite
===================================
Phase 1: Tests for the health endpoint only.
Algorithm + ML tests added in Phases 2 and 3.
"""

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
async def client():
    """Async test client for the FastAPI app."""
    from app.main import app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_returns_ok(client):
    response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_health_returns_version(client):
    response = await client.get("/api/health")
    assert "version" in response.json()


@pytest.mark.asyncio
async def test_health_returns_message(client):
    response = await client.get("/api/health")
    assert "message" in response.json()


@pytest.mark.asyncio
async def test_health_content_type_json(client):
    response = await client.get("/api/health")
    assert "application/json" in response.headers["content-type"]


@pytest.mark.asyncio
async def test_docs_reachable(client):
    """Swagger UI should be reachable."""
    response = await client.get("/docs")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_unknown_route_returns_404(client):
    response = await client.get("/api/nonexistent")
    assert response.status_code == 404
