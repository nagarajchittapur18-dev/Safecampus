"""
SafeCampus AI — Unit Tests: Machine Learning Crowd Prediction
=============================================================
Tests:
1. Synthetic dataset integrity (schema, required columns, valid values).
2. ML artifacts existence & comparison metrics validity.
3. CrowdPredictionService inference & probability properties.
4. REST API endpoint GET /api/crowd/prediction/{location_id}.
"""

from __future__ import annotations

from pathlib import Path
import pandas as pd
import pytest
from httpx import ASGITransport, AsyncClient

from app.services.crowd_service import (
    CrowdPredictionResult,
    get_crowd_service,
    reset_crowd_service,
)

# Project root paths
_REPO_ROOT = Path(__file__).resolve().parents[2]
_DATA_CSV = _REPO_ROOT / "ml" / "data" / "crowd_data.csv"
_COMPARISON_CSV = _REPO_ROOT / "ml" / "results" / "model_comparison.csv"
_CONFUSION_PNG = _REPO_ROOT / "ml" / "results" / "confusion_matrix.png"
_IMPORTANCE_PNG = _REPO_ROOT / "ml" / "results" / "feature_importance.png"
_MODEL_FILE = _REPO_ROOT / "ml" / "models" / "crowd_model.joblib"


# ---------------------------------------------------------------------------
# 1. Dataset Integrity Tests
# ---------------------------------------------------------------------------

class TestCrowdDataset:
    def test_dataset_exists_and_non_empty(self):
        assert _DATA_CSV.exists(), "crowd_data.csv missing from ml/data/"
        df = pd.read_csv(_DATA_CSV)
        assert len(df) >= 1000, f"Dataset too small: {len(df)} rows"

    def test_required_columns_present(self):
        df = pd.read_csv(_DATA_CSV)
        required_cols = [
            "timestamp",
            "date",
            "hour",
            "day_of_week",
            "location_id",
            "event_flag",
            "class_activity",
            "exam_flag",
            "holiday_flag",
            "historical_crowd",
            "crowd_level",
        ]
        for col in required_cols:
            assert col in df.columns, f"Missing column: {col}"

    def test_target_classes_represented(self):
        df = pd.read_csv(_DATA_CSV)
        unique_classes = set(df["crowd_level"].unique())
        expected_classes = {"LOW", "MEDIUM", "HIGH", "VERY_HIGH"}
        assert expected_classes.issubset(unique_classes), (
            f"Expected classes {expected_classes} but got {unique_classes}"
        )

    def test_feature_value_ranges(self):
        df = pd.read_csv(_DATA_CSV)
        assert df["hour"].between(0, 23).all()
        assert df["day_of_week"].between(0, 6).all()
        assert df["location_id"].between(1, 20).all()
        assert df["event_flag"].isin([0, 1]).all()
        assert df["class_activity"].isin([0, 1]).all()
        assert df["exam_flag"].isin([0, 1]).all()
        assert df["holiday_flag"].isin([0, 1]).all()
        assert df["historical_crowd"].between(0.0, 1.0).all()


# ---------------------------------------------------------------------------
# 2. ML Artifacts & Comparison Tests
# ---------------------------------------------------------------------------

class TestMLArtifacts:
    def test_model_artifact_exists(self):
        assert _MODEL_FILE.exists(), "crowd_model.joblib missing from ml/models/"

    def test_visualizations_exist(self):
        assert _CONFUSION_PNG.exists(), "confusion_matrix.png missing from ml/results/"
        assert _IMPORTANCE_PNG.exists(), "feature_importance.png missing from ml/results/"

    def test_model_comparison_contains_all_four_models(self):
        assert _COMPARISON_CSV.exists(), "model_comparison.csv missing"
        comp_df = pd.read_csv(_COMPARISON_CSV)
        expected_models = {
            "Logistic Regression",
            "Decision Tree",
            "Random Forest",
            "Gradient Boosting",
        }
        present_models = set(comp_df["model"].unique())
        assert expected_models.issubset(present_models), (
            f"Missing required models in comparison. Expected {expected_models}, got {present_models}"
        )

    def test_metrics_in_valid_range(self):
        comp_df = pd.read_csv(_COMPARISON_CSV)
        for metric in ["accuracy", "f1_weighted", "precision_weighted", "recall_weighted"]:
            assert comp_df[metric].between(0.0, 1.0).all()


# ---------------------------------------------------------------------------
# 3. CrowdPredictionService Tests
# ---------------------------------------------------------------------------

class TestCrowdService:
    def setup_method(self):
        reset_crowd_service()

    def test_service_prediction_output(self):
        service = get_crowd_service()
        res = service.predict(location_id=1, hour=12, day_of_week=2)

        assert isinstance(res, CrowdPredictionResult)
        assert res.location_id == 1
        assert res.predicted_crowd_level in ["LOW", "MEDIUM", "HIGH", "VERY_HIGH"]
        assert 0.0 <= res.predicted_crowd_score <= 1.0
        assert 0.0 <= res.confidence <= 1.0
        assert res.is_synthetic_model is True

        # Class probabilities should sum to ~1.0
        prob_sum = sum(res.class_probabilities.values())
        assert prob_sum == pytest.approx(1.0, abs=1e-3)

    def test_service_invalid_hour_raises(self):
        service = get_crowd_service()
        with pytest.raises(ValueError, match="hour"):
            service.predict(location_id=1, hour=25)

    def test_service_invalid_day_raises(self):
        service = get_crowd_service()
        with pytest.raises(ValueError, match="day_of_week"):
            service.predict(location_id=1, day_of_week=9)


# ---------------------------------------------------------------------------
# 4. API Tests: GET /api/crowd/prediction/{location_id}
# ---------------------------------------------------------------------------

class TestCrowdAPI:
    @pytest.fixture
    async def client(self):
        from app.main import app
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
            yield ac

    @pytest.mark.asyncio
    async def test_predict_endpoint_success(self, client):
        resp = await client.get("/api/crowd/prediction/1")
        assert resp.status_code == 200
        data = resp.json()

        assert data["location_id"] == 1
        assert data["location_name"] == "Main Gate"
        assert data["predicted_crowd_level"] in ["LOW", "MEDIUM", "HIGH", "VERY_HIGH"]
        assert 0.0 <= data["predicted_crowd_score"] <= 1.0
        assert 0.0 <= data["confidence"] <= 1.0
        assert "class_probabilities" in data
        assert "features_used" in data
        assert data["is_synthetic_model"] is True

    @pytest.mark.asyncio
    async def test_predict_endpoint_with_overrides(self, client):
        resp = await client.get(
            "/api/crowd/prediction/8?hour=13&day_of_week=1&class_activity=1"
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["location_id"] == 8
        assert data["location_name"] == "Canteen"
        assert data["features_used"]["hour"] == 13
        assert data["features_used"]["class_activity"] == 1

    @pytest.mark.asyncio
    async def test_predict_endpoint_location_not_found(self, client):
        resp = await client.get("/api/crowd/prediction/9999")
        assert resp.status_code == 404
        assert "detail" in resp.json()

    @pytest.mark.asyncio
    async def test_predict_endpoint_invalid_hour_validation_error(self, client):
        resp = await client.get("/api/crowd/prediction/1?hour=30")
        assert resp.status_code == 422
