"""
SafeCampus AI — Pydantic Schemas for Crowd Prediction
"""

from __future__ import annotations

from typing import Any, Dict
from pydantic import BaseModel, Field


class CrowdPredictionResponse(BaseModel):
    """Schema returned by GET /api/crowd/prediction/{location_id}."""

    location_id: int
    location_name: str = Field(..., description="Campus node location name")
    predicted_crowd_level: str = Field(..., description="Categorical prediction: LOW, MEDIUM, HIGH, VERY_HIGH")
    predicted_crowd_score: float = Field(..., description="Continuous expected crowd density score in [0, 1]")
    confidence: float = Field(..., description="Confidence score / highest class probability in [0, 1]")
    class_probabilities: Dict[str, float] = Field(..., description="Probabilities for each crowd category")
    features_used: Dict[str, Any] = Field(..., description="Contextual features fed into the ML model")
    model_name: str = Field(..., description="Underlying machine learning model name")
    is_synthetic_model: bool = Field(True, description="Indicates model was trained on synthetic academic data")
