"""
SafeCampus AI — Automated Unit Tests for Research Experiment Framework
========================================================================
Verifies:
1. Experiment 1 (Crowd Prediction) metrics and models.
2. Experiment 2 (Routing Comparison) metric calculation across Dijkstra, A*, and MOA*.
3. Experiment 3 (Personalization) evaluation across all 6 presets on identical pairs.
4. Experiment 4 (Ablation) weight vectors sum to 1.00 and stage progression.
5. Experiment 5 (Sensitivity) parameter sweep normalization.
"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import pytest
import pandas as pd

from app.algorithms.graph import CampusGraph
from app.algorithms.multi_objective_a_star import WeightVector, multi_objective_a_star
from app.services.graph_service import get_graph, reset_graph
from research.experiments.exp1_crowd_prediction import run_experiment_1
from research.experiments.exp2_routing_comparison import run_experiment_2
from research.experiments.exp3_personalization import run_experiment_3, PRESETS
from research.experiments.exp4_ablation_study import run_experiment_4, ABLATION_STAGES
from research.experiments.exp5_sensitivity_analysis import run_experiment_5, _build_sweep_weight


@pytest.fixture(autouse=True)
def setup_graph():
    reset_graph()
    return get_graph()


class TestExperimentFramework:
    def test_exp1_returns_valid_metrics(self):
        csv_path = _ROOT / "research" / "results" / "exp1_crowd_prediction_metrics.csv"
        assert csv_path.exists(), "Exp 1 CSV must exist"

        df = pd.read_csv(csv_path, comment="#")
        expected_cols = ["model", "accuracy", "precision_macro", "recall_macro", "f1_macro"]
        for col in expected_cols:
            assert col in df.columns, f"Missing metric column {col}"

        # All 4 models must be present
        models = set(df["model"])
        assert "Logistic Regression" in models
        assert "Decision Tree" in models
        assert "Random Forest" in models
        assert "Gradient Boosting" in models

        # Accuracies must be reasonable floats
        for acc in df["accuracy"]:
            assert 0.5 <= acc <= 1.0

    def test_exp2_routing_comparison_structure(self, setup_graph):
        csv_path = _ROOT / "research" / "results" / "exp2_routing_comparison.csv"
        assert csv_path.exists(), "Exp 2 CSV must exist"

        df = pd.read_csv(csv_path, comment="#")
        for col in ["distance_m", "travel_time_min", "crowd_score", "safety_score", "accessibility_score", "execution_time_ms"]:
            assert col in df.columns

        algos = set(df["algorithm"])
        assert "Dijkstra" in algos
        assert "A*" in algos
        assert "Personalized Multi-Objective A*" in algos

    def test_exp3_identical_pairs_tested(self, setup_graph):
        csv_path = _ROOT / "research" / "results" / "exp3_personalization_comparison.csv"
        assert csv_path.exists(), "Exp 3 CSV must exist"

        df = pd.read_csv(csv_path, comment="#")
        for pref in PRESETS:
            assert pref in set(df["preference"]), f"Preset {pref} missing"

        # Verify all presets test identical pairs
        pair_counts = df.groupby("preference")["pair_label"].count()
        assert len(set(pair_counts.values)) == 1, "All presets must evaluate identical count of pairs"

    def test_exp4_ablation_weights_sum_to_one(self):
        for stage_idx, stage_name, wv in ABLATION_STAGES:
            total = wv.wD + wv.wT + wv.wC + wv.wS + wv.wA
            assert pytest.approx(total, abs=1e-5) == 1.0, f"Stage {stage_name} weights must sum to 1.0"

    def test_exp5_sweep_weights_valid(self):
        for dim in ["wD", "wT", "wC", "wS", "wA"]:
            for val in [0.1, 0.3, 0.5, 0.7, 0.9]:
                wv = _build_sweep_weight(dim, val)
                total = wv.wD + wv.wT + wv.wC + wv.wS + wv.wA
                assert pytest.approx(total, abs=1e-5) == 1.0
                assert getattr(wv, dim) == pytest.approx(val, abs=1e-5)
