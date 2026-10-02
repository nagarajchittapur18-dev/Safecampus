"""
SafeCampus AI — Locations Router
GET /api/locations         → list all campus locations
GET /api/locations/{id}    → single location by ID
"""

from fastapi import APIRouter, HTTPException

from app.schemas.location import LocationListResponse, LocationResponse
from app.services.graph_service import get_graph

router = APIRouter()


def _node_to_response(node) -> LocationResponse:
    return LocationResponse(
        id=node.id,
        name=node.name,
        latitude=node.latitude,
        longitude=node.longitude,
        location_type=node.node_type,
        description=node.description,
    )


@router.get(
    "",
    response_model=LocationListResponse,
    summary="List all campus locations",
)
async def list_locations() -> LocationListResponse:
    """
    Returns every node in the campus graph.
    Useful for populating search dropdowns and map markers.
    """
    graph = get_graph()
    nodes = sorted(graph.all_nodes(), key=lambda n: n.id)
    return LocationListResponse(
        count=len(nodes),
        locations=[_node_to_response(n) for n in nodes],
    )


@router.get(
    "/{location_id}",
    response_model=LocationResponse,
    summary="Get a specific campus location",
)
async def get_location(location_id: int) -> LocationResponse:
    """
    Returns a single campus location by its node ID.
    Returns 404 if the location does not exist.
    """
    graph = get_graph()
    node = graph.get_node(location_id)
    if node is None:
        raise HTTPException(
            status_code=404,
            detail=f"Location with id={location_id} not found.",
        )
    return _node_to_response(node)
