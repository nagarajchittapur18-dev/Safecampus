"""
SafeCampus AI — Pydantic Schemas for Locations
"""

from typing import List
from pydantic import BaseModel, Field


class LocationResponse(BaseModel):
    """Schema returned by GET /api/locations and GET /api/locations/{id}."""

    id: int
    name: str
    latitude: float
    longitude: float
    location_type: str   # the public field name in the API response
    description: str

    model_config = {"populate_by_name": True}


class LocationListResponse(BaseModel):
    count: int
    locations: List[LocationResponse]
