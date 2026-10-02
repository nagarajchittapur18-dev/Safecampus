"""
SafeCampus AI — Campus Crowd Prediction Service
================================================
Provides reusable ML-based crowd prediction inference.
Loads the trained model (`ml/models/crowd_model.joblib`), scaler, and label encoder.

DISCLAIMER:
Inference is powered by a model trained on synthetic campus crowd patterns.
It represents reproducible research simulation data and not actual physical
sensor measurements.
"""

from __future__ import annotations

import datetime
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import joblib
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# Default model directory relative to repository root
_REPO_ROOT = Path(__file__).resolve().parents[3]
_DEFAULT_MODELS_DIR = _REPO_ROOT / "ml" / "models"


@dataclass(frozen=True)
class CrowdPredictionResult:
    """Immutable result structure from the crowd prediction service."""

    location_id: int
    predicted_crowd_level: str          # "LOW", "MEDIUM", "HIGH", "VERY_HIGH"
    predicted_crowd_score: float        # Expected continuous crowd cost in [0, 1]
    confidence: float                   # Highest class probability [0, 1]
    class_probabilities: Dict[str, float]
    features_used: Dict[str, any]
    model_name: str
    is_synthetic_model: bool = True     # Explicit academic research disclosure


_crowd_service_instance: Optional[CrowdPredictionService] = None


def get_crowd_service() -> CrowdPredictionService:
    """Returns singleton instance of CrowdPredictionService."""
    global _crowd_service_instance
    if _crowd_service_instance is None:
        _crowd_service_instance = CrowdPredictionService()
    return _crowd_service_instance


def reset_crowd_service() -> None:
    """Resets the singleton instance (useful in testing)."""
    global _crowd_service_instance
    _crowd_service_instance = None


class CrowdPredictionService:
    """
    Reusable prediction service wrapping the pre-trained ML model,
    feature scaler, and label encoder.
    """

    # Representative crowd score weights for expected crowd value
    CLASS_WEIGHTS = {
        "LOW": 0.15,
        "MEDIUM": 0.40,
        "HIGH": 0.65,
        "VERY_HIGH": 0.90,
    }

    def __init__(self, models_dir: Optional[Path] = None) -> None:
        self.models_dir = Path(models_dir) if models_dir else _DEFAULT_MODELS_DIR
        self._load_artifacts()

    def _load_artifacts(self) -> None:
        model_file = self.models_dir / "crowd_model.joblib"
        scaler_file = self.models_dir / "scaler.joblib"
        encoder_file = self.models_dir / "label_encoder.joblib"
        metadata_file = self.models_dir / "metadata.json"

        if not model_file.exists():
            raise FileNotFoundError(
                f"Model artifact not found at {model_file}. Run ml/train.py first."
            )

        self.model = joblib.load(model_file)
        self.scaler = joblib.load(scaler_file) if scaler_file.exists() else None
        self.label_encoder = joblib.load(encoder_file)

        if metadata_file.exists():
            with open(metadata_file, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {"features": [], "classes": list(self.label_encoder.classes_)}

        self.model_name = type(self.model).__name__
        logger.info("Loaded crowd prediction model: %s from %s", self.model_name, self.models_dir)

    def predict(
        self,
        location_id: int,
        hour: Optional[int] = None,
        day_of_week: Optional[int] = None,
        event_flag: int = 0,
        class_activity: Optional[int] = None,
        exam_flag: int = 0,
        holiday_flag: int = 0,
        historical_crowd: Optional[float] = None,
    ) -> CrowdPredictionResult:
        """
        Executes ML crowd level inference for a given location and temporal context.
        """
        now = datetime.datetime.now()

        if hour is None:
            hour = now.hour
        if not (0 <= hour <= 23):
            raise ValueError(f"hour must be between 0 and 23, got {hour}")

        if day_of_week is None:
            day_of_week = now.weekday()
        if not (0 <= day_of_week <= 6):
            raise ValueError(f"day_of_week must be between 0 and 6, got {day_of_week}")

        is_weekend = day_of_week in (5, 6)

        # Default class activity based on standard campus academic schedule
        if class_activity is None:
            if not is_weekend and not holiday_flag and not exam_flag and (9 <= hour <= 16):
                class_activity = 1
            else:
                class_activity = 0

        # Default historical crowd baseline
        if historical_crowd is None:
            if class_activity or (12 <= hour <= 14):
                historical_crowd = 0.55
            elif 8 <= hour <= 19 and not is_weekend:
                historical_crowd = 0.35
            else:
                historical_crowd = 0.15

        features_dict = {
            "hour": hour,
            "day_of_week": day_of_week,
            "location_id": location_id,
            "event_flag": int(event_flag),
            "class_activity": int(class_activity),
            "exam_flag": int(exam_flag),
            "holiday_flag": int(holiday_flag),
            "historical_crowd": float(historical_crowd),
        }

        # Build feature DataFrame with exact feature names expected by preprocessor
        feature_df = pd.DataFrame([features_dict])

        if self.scaler is not None:
            X_input = self.scaler.transform(feature_df)
        else:
            X_input = feature_df.values

        # Model inference
        pred_idx = self.model.predict(X_input)[0]
        predicted_level = self.label_encoder.inverse_transform([pred_idx])[0]

        # Probabilities
        if hasattr(self.model, "predict_proba"):
            probs = self.model.predict_proba(X_input)[0]
            classes = self.label_encoder.classes_
            class_prob_dict = {
                cls_name: round(float(probs[i]), 4)
                for i, cls_name in enumerate(classes)
            }
            confidence = round(float(np.max(probs)), 4)

            # Compute expected continuous crowd cost in [0, 1]
            expected_score = sum(
                class_prob_dict.get(k, 0.0) * weight
                for k, weight in self.CLASS_WEIGHTS.items()
            )
            expected_score = round(float(np.clip(expected_score, 0.0, 1.0)), 4)
        else:
            confidence = 1.0
            class_prob_dict = {predicted_level: 1.0}
            expected_score = self.CLASS_WEIGHTS.get(predicted_level, 0.50)

        return CrowdPredictionResult(
            location_id=location_id,
            predicted_crowd_level=predicted_level,
            predicted_crowd_score=expected_score,
            confidence=confidence,
            class_probabilities=class_prob_dict,
            features_used=features_dict,
            model_name=self.model_name,
            is_synthetic_model=True,
        )
