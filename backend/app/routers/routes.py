"""
SafeCampus AI — Routes Router
POST /api/routes/dijkstra   → Dijkstra shortest-path route
POST /api/routes/a-star     → A* shortest-path route
POST /api/routes/recommend  → Personalized Multi-Objective A* safe route
"""

from fastapi import APIRouter, HTTPException, status

from app.algorithms.dijkstra import NodeNotFoundError, NoPathError
from app.schemas.route import (
    AStarRequest,
    AStarResponse,
    DijkstraRequest,
    DijkstraResponse,
    ExplainRouteResponse,
    RecommendRouteRequest,
    RecommendRouteResponse,
    RouteExplanation,
)
from app.services.route_service import RouteService

router = APIRouter()
_route_service = RouteService()


@router.post(
    "/dijkstra",
    response_model=DijkstraResponse,
    status_code=status.HTTP_200_OK,
    summary="Dijkstra shortest-distance route",
    description=(
        "Finds the shortest-distance path between two campus nodes "
        "using Dijkstra's algorithm. "
        "Edge weight = physical distance in metres. "
        "Travel time is the sum of edge base_time values along the path."
    ),
)
async def dijkstra_route(request: DijkstraRequest) -> DijkstraResponse:
    """
    Compute a shortest-distance campus route using Dijkstra's algorithm.

    - **source_id**: Starting campus node ID.
    - **destination_id**: Destination campus node ID.

    Returns the ordered path, total distance (m), and estimated travel time (min).
    """
    try:
        return _route_service.find_dijkstra(
            source_id=request.source_id,
            destination_id=request.destination_id,
        )

    except NodeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except NoPathError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.post(
    "/a-star",
    response_model=AStarResponse,
    status_code=status.HTTP_200_OK,
    summary="A* shortest-distance route",
    description=(
        "Finds the shortest-distance path between two campus nodes "
        "using A* search with straight-line Haversine heuristic. "
        "Edge weight = physical distance in metres. "
        "Returns route, distance, travel time, and execution time in ms."
    ),
)
async def a_star_route(request: AStarRequest) -> AStarResponse:
    """
    Compute a shortest-distance campus route using A* search.

    - **source_id**: Starting campus node ID.
    - **destination_id**: Destination campus node ID.

    Returns the ordered path, total distance (m), estimated travel time (min),
    and execution time (ms).
    """
    try:
        return _route_service.find_a_star(
            source_id=request.source_id,
            destination_id=request.destination_id,
        )

    except NodeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except NoPathError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.post(
    "/recommend",
    response_model=RecommendRouteResponse,
    status_code=status.HTTP_200_OK,
    summary="Personalized Multi-Objective Safe Route Recommendation",
    description=(
        "Computes a personalized Pareto-optimal safe campus route using Multi-Objective A*. "
        "Considers: distance, travel time, crowd density, safety, and accessibility. "
        "Supports preference presets (shortest, fastest, safest, least_crowded, accessible, balanced) "
        "or custom weight vectors."
    ),
)
async def recommend_route(request: RecommendRouteRequest) -> RecommendRouteResponse:
    """
    Compute a personalized multi-objective recommended campus route.

    - **source_id**: Starting campus node ID.
    - **destination_id**: Destination campus node ID.
    - **preference**: Preference preset ('shortest', 'fastest', 'safest', 'least_crowded', 'accessible', 'balanced').
    - **weights**: Optional custom weight dictionary {wD, wT, wC, wS, wA}.
    """
    try:
        return _route_service.recommend_route(
            source_id=request.source_id,
            destination_id=request.destination_id,
            preference=request.preference,
            custom_weights=request.weights,
            hour=request.hour,
            day_of_week=request.day_of_week,
            event_flag=request.event_flag,
            class_activity=request.class_activity,
            exam_flag=request.exam_flag,
            holiday_flag=request.holiday_flag,
            use_ml_crowd=request.use_ml_crowd,
        )

    except NodeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except (NoPathError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.post(
    "/explain",
    response_model=ExplainRouteResponse,
    status_code=status.HTTP_200_OK,
    summary="Route Recommendation Dynamic Explanation & Trade-Off Analysis",
    description=(
        "Computes a recommended safe route and dynamically explains why it was selected, "
        "including exact quantified trade-offs against the ground-truth Dijkstra shortest path. "
        "Calculates distance, time, crowd, safety, and accessibility deltas without hardcoded values."
    ),
)
async def explain_route(request: RecommendRouteRequest) -> ExplainRouteResponse:
    """
    Dynamically explain a recommended route against the shortest path baseline.

    - **source_id**: Starting campus node ID.
    - **destination_id**: Destination campus node ID.
    - **preference**: Preference preset ('shortest', 'fastest', 'safest', 'least_crowded', 'accessible', 'balanced').
    - **weights**: Optional custom weight dictionary.
    """
    try:
        rec_response = _route_service.recommend_route(
            source_id=request.source_id,
            destination_id=request.destination_id,
            preference=request.preference,
            custom_weights=request.weights,
            hour=request.hour,
            day_of_week=request.day_of_week,
            event_flag=request.event_flag,
            class_activity=request.class_activity,
            exam_flag=request.exam_flag,
            holiday_flag=request.holiday_flag,
            use_ml_crowd=request.use_ml_crowd,
        )

        if rec_response.explanation is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Explanation engine could not generate trade-off analysis.",
            )

        return ExplainRouteResponse(
            source_id=rec_response.source_id,
            destination_id=rec_response.destination_id,
            preference=rec_response.preference,
            explanation=rec_response.explanation,
            recommendation=rec_response,
        )

    except NodeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except (NoPathError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

