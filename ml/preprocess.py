"""
SafeCampus AI — Machine Learning Preprocessing Pipeline
========================================================
Handles feature extraction, label encoding, scaling, and train-test splitting
for campus crowd density classification.

Features:
- hour (0-23)
- day_of_week (0-6)
- location_id (1-20)
- event_flag (0/1)
- class_activity (0/1)
- exam_flag (0/1)
- holiday_flag (0/1)
- historical_crowd (float [0, 1])

Target:
- crowd_level: {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "VERY_HIGH": 3}
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

# Feature definition
FEATURE_COLUMNS: List[str] = [
    "hour",
    "day_of_week",
    "location_id",
    "event_flag",
    "class_activity",
    "exam_flag",
    "holiday_flag",
    "historical_crowd",
]

TARGET_COLUMN: str = "crowd_level"

# Ordered class names
CROWD_CLASSES: List[str] = ["LOW", "MEDIUM", "HIGH", "VERY_HIGH"]


def get_label_encoder() -> LabelEncoder:
    """Returns a deterministic fitted LabelEncoder matching CROWD_CLASSES."""
    le = LabelEncoder()
    le.fit(CROWD_CLASSES)
    return le


def load_dataset(data_path: str = "ml/data/crowd_data.csv") -> pd.DataFrame:
    """Loads crowd dataset from disk."""
    p = Path(data_path)
    if not p.exists():
        raise FileNotFoundError(f"Dataset not found at {data_path}. Run generate_dataset.py first.")
    return pd.read_csv(p)


def prepare_features_and_target(
    df: pd.DataFrame,
) -> Tuple[pd.DataFrame, np.ndarray, LabelEncoder]:
    """Extracts feature matrix X, encoded target y, and the label encoder."""
    X = df[FEATURE_COLUMNS].copy()
    y_raw = df[TARGET_COLUMN].copy()

    le = get_label_encoder()
    y = le.transform(y_raw)

    return X, y, le


def split_and_scale_data(
    X: pd.DataFrame,
    y: np.ndarray,
    test_size: float = 0.20,
    random_state: int = 42,
    scale: bool = True,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, StandardScaler | None]:
    """
    Splits into train/test sets (stratified) and optionally standard-scales features.
    """
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    scaler = None
    if scale:
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        return X_train_scaled, X_test_scaled, y_train, y_test, scaler

    return X_train.values, X_test.values, y_train, y_test, None


def save_preprocessing_artifacts(
    scaler: StandardScaler | None,
    le: LabelEncoder,
    models_dir: str = "ml/models",
) -> None:
    """Saves scaler, label encoder, and feature column metadata."""
    out_dir = Path(models_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if scaler is not None:
        joblib.dump(scaler, out_dir / "scaler.joblib")

    joblib.dump(le, out_dir / "label_encoder.joblib")

    meta = {
        "features": FEATURE_COLUMNS,
        "classes": CROWD_CLASSES,
        "scaler_used": scaler is not None,
    }
    with open(out_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    print(f"Saved preprocessing artifacts to {out_dir}")
