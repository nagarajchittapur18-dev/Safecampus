"""SafeCampus AI — Health Router"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    version: str
    message: str


@router.get("/health", response_model=HealthResponse, summary="Health check")
async def health_check() -> HealthResponse:
    """
    Returns the API health status.

    Used by monitoring tools, the Flutter app on startup, and CI pipelines
    to verify the backend is reachable.
    """
    return HealthResponse(
        status="ok",
        version="0.1.0",
        message="SafeCampus AI backend is running.",
    )
