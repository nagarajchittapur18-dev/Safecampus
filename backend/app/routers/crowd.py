"""
SafeCampus AI — Crowd Router
=============================
Provides real-time and scheduled ML crowd prediction endpoints.
GET /api/crowd/prediction/{location_id}
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.crowd import CrowdPredictionResponse
from app.services.crowd_service import get_crowd_service
from app.services.graph_service import get_graph

router = APIRouter()


@router.get(
    "/prediction/{location_id}",
    response_model=CrowdPredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Predict crowd level for a campus location",
    description=(
        "Executes ML crowd inference for a given campus location node ID. "
        "Allows supplying temporal and contextual overrides (hour, day of week, "
        "events, classes, exams, holidays). If parameters are omitted, current "
        "temporal context is automatically inferred."
    ),
)
async def predict_location_crowd(
    location_id: int,
    hour: Optional[int] = Query(None, ge=0, le=23, description="Hour of day (0-23)"),
    day_of_week: Optional[int] = Query(None, ge=0, le=6, description="0=Mon ... 6=Sun"),
    event_flag: int = Query(0, ge=0, le=1, description="1 if special event active"),
    class_activity: Optional[int] = Query(None, ge=0, le=1, description="1 if classes in session"),
    exam_flag: int = Query(0, ge=0, le=1, description="1 if examination period"),
    holiday_flag: int = Query(0, ge=0, le=1, description="1 if campus holiday"),
    historical_crowd: Optional[float] = Query(None, ge=0.0, le=1.0, description="Optional previous crowd baseline"),
) -> CrowdPredictionResponse:
    """
    Predicts crowd category and expected density score for location_id.
    """
    graph = get_graph()
    node = graph.get_node(location_id)
    if node is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location with id={location_id} not found in campus graph.",
        )

    try:
        crowd_service = get_crowd_service()
        pred_res = crowd_service.predict(
            location_id=location_id,
            hour=hour,
            day_of_week=day_of_week,
            event_flag=event_flag,
            class_activity=class_activity,
            exam_flag=exam_flag,
            holiday_flag=holiday_flag,
            historical_crowd=historical_crowd,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing crowd prediction: {str(exc)}",
        ) from exc

    return CrowdPredictionResponse(
        location_id=pred_res.location_id,
        location_name=node.name,
        predicted_crowd_level=pred_res.predicted_crowd_level,
        predicted_crowd_score=pred_res.predicted_crowd_score,
        confidence=pred_res.confidence,
        class_probabilities=pred_res.class_probabilities,
        features_used=pred_res.features_used,
        model_name=pred_res.model_name,
        is_synthetic_model=pred_res.is_synthetic_model,
    )
