"""
SafeCampus AI — Research Experiment 1: Crowd Prediction Model Comparison
=========================================================================
Academic Experiment:
Compares four supervised machine learning algorithms for campus crowd density
classification across diurnal and event-driven patterns.

Algorithms:
1. Logistic Regression (Linear Baseline)
2. Decision Tree (Non-linear Baseline)
3. Random Forest (Ensemble Bagging)
4. Gradient Boosting (Ensemble Boosting)

Metrics:
- Accuracy
- Precision (Macro & Weighted)
- Recall (Macro & Weighted)
- F1-Score (Macro & Weighted)
- Training Time & Inference Latency

DATA ORIGIN & SCIENTIFIC INTEGRITY DISCLAIMER:
---------------------------------------------
This experiment utilizes synthetic campus simulation data generated with a fixed
pseudorandom seed (42). Features represent controlled distributions across campus
facility types, hours of day, exam periods, and events.
It does NOT represent physical IoT sensor measurements from live human subjects.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# Add project root and backend to sys.path
_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from typing import Any, Dict, List, Tuple

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.tree import DecisionTreeClassifier

from ml.generate_dataset import generate_crowd_dataset
from ml.preprocess import (
    load_dataset,
    prepare_features_and_target,
    split_and_scale_data,
)

DISCLAIMER_TEXT = (
    "DATA ORIGIN: Synthetic campus crowd simulation (Seed: 42). "
    "Controlled academic simulation; not empirical physical IoT sensor tracking."
)


def run_experiment_1(
    data_path: str = "ml/data/crowd_data.csv",
    results_dir: str = "research/results",
    figures_dir: str = "research/figures",
    random_state: int = 42,
) -> pd.DataFrame:
    """
    Executes Experiment 1: Multiclass model training, validation, and metric comparison.
    """
    res_path = Path(results_dir)
    fig_path = Path(figures_dir)
    res_path.mkdir(parents=True, exist_ok=True)
    fig_path.mkdir(parents=True, exist_ok=True)

    # 1. Load or generate synthetic dataset
    csv_file = Path(data_path)
    if not csv_file.exists():
        print(f"[Exp 1] Dataset not found at {data_path}. Generating synthetic data...")
        generate_crowd_dataset(num_days=30, output_path=str(csv_file), seed=random_state)

    print(f"[Exp 1] Loading dataset from {data_path}...")
    df = load_dataset(str(csv_file))
    print(f"[Exp 1] Dataset contains {len(df):,} samples across {df['location_id'].nunique()} locations.")

    X, y, le = prepare_features_and_target(df)
    class_names: List[str] = list(le.classes_)

    # 80/20 train/test split with standard scaling
    X_train, X_test, y_train, y_test, _ = split_and_scale_data(
        X, y, test_size=0.20, random_state=random_state, scale=True
    )

    models: Dict[str, Any] = {
        "Logistic Regression": LogisticRegression(
            max_iter=1000,
            random_state=random_state,
        ),
        "Decision Tree": DecisionTreeClassifier(
            max_depth=12,
            random_state=random_state,
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=100,
            max_depth=16,
            random_state=random_state,
            n_jobs=-1,
        ),
        "Gradient Boosting": GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=random_state,
        ),
    }

    records: List[Dict[str, Any]] = []
    confusion_matrices: Dict[str, np.ndarray] = {}

    print(f"\n[Exp 1] Training and benchmarking {len(models)} candidate models...")
    print("=" * 80)

    for name, model in models.items():
        # Measure training duration
        t0 = time.perf_counter()
        model.fit(X_train, y_train)
        train_time_sec = time.perf_counter() - t0

        # Measure inference latency
        t1 = time.perf_counter()
        y_pred = model.predict(X_test)
        inference_time_ms = ((time.perf_counter() - t1) / len(X_test)) * 1000.0

        # Compute metrics
        acc = accuracy_score(y_test, y_pred)
        prec_macro = precision_score(y_test, y_pred, average="macro", zero_division=0)
        prec_weighted = precision_score(y_test, y_pred, average="weighted", zero_division=0)
        rec_macro = recall_score(y_test, y_pred, average="macro", zero_division=0)
        rec_weighted = recall_score(y_test, y_pred, average="weighted", zero_division=0)
        f1_macro = f1_score(y_test, y_pred, average="macro", zero_division=0)
        f1_weighted = f1_score(y_test, y_pred, average="weighted", zero_division=0)

        cm = confusion_matrix(y_test, y_pred)
        confusion_matrices[name] = cm

        records.append({
            "model": name,
            "accuracy": round(acc, 4),
            "precision_macro": round(prec_macro, 4),
            "precision_weighted": round(prec_weighted, 4),
            "recall_macro": round(rec_macro, 4),
            "recall_weighted": round(rec_weighted, 4),
            "f1_macro": round(f1_macro, 4),
            "f1_weighted": round(f1_weighted, 4),
            "train_time_sec": round(train_time_sec, 3),
            "inference_latency_ms": round(inference_time_ms, 4),
            "data_type": "SYNTHETIC",
        })

        print(
            f"{name:<22} | Acc: {acc:.4f} | Prec: {prec_macro:.4f} | "
            f"Recall: {rec_macro:.4f} | F1: {f1_macro:.4f} | "
            f"Train: {train_time_sec:.2f}s | Latency: {inference_time_ms:.3f}ms"
        )

    print("=" * 80)

    results_df = pd.DataFrame(records).sort_values(by="f1_macro", ascending=False)

    # Save CSV Results
    csv_out = res_path / "exp1_crowd_prediction_metrics.csv"
    with open(csv_out, "w", encoding="utf-8") as f:
        f.write(f"# {DISCLAIMER_TEXT}\n")
        results_df.to_csv(f, index=False)
    print(f"\n[Exp 1] Saved metrics CSV to {csv_out}")

    # Generate Model Comparison Bar Chart
    _plot_model_comparison(results_df, fig_path / "exp1_model_comparison.png")

    # Generate Confusion Matrix Multi-plot
    _plot_confusion_matrices(confusion_matrices, class_names, fig_path / "exp1_confusion_matrices.png")

    return results_df


def _plot_model_comparison(df: pd.DataFrame, out_path: Path) -> None:
    """Generates comparison bar chart across Accuracy, Precision, Recall, and F1."""
    models = df["model"].tolist()
    metrics = ["accuracy", "precision_macro", "recall_macro", "f1_macro"]
    labels = ["Accuracy", "Precision (Macro)", "Recall (Macro)", "F1-Score (Macro)"]
    colors = ["#1976D2", "#00897B", "#FFA000", "#7B1FA2"]

    x = np.arange(len(models))
    width = 0.18

    fig, ax = plt.subplots(figsize=(10, 6))

    for i, (metric, label, col) in enumerate(zip(metrics, labels, colors)):
        vals = df[metric].tolist()
        rects = ax.bar(x + (i - 1.5) * width, vals, width, label=label, color=col, edgecolor="black", linewidth=0.5)
        for rect in rects:
            height = rect.get_height()
            ax.annotate(
                f"{height:.2f}",
                xy=(rect.get_x() + rect.get_width() / 2, height),
                xytext=(0, 2),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=8,
                rotation=45,
            )

    ax.set_title("Experiment 1 — Crowd Prediction Model Comparison\n(Multiclass Classification Performance)", fontsize=13, pad=14, fontweight="bold")
    ax.set_ylabel("Score [0.0 - 1.0]", fontsize=11)
    ax.set_xticks(x)
    ax.set_xticklabels(models, fontsize=10, fontweight="bold")
    ax.set_ylim(0, 1.15)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    ax.legend(loc="lower right", framealpha=0.95)

    # Academic Disclaimer in footnote
    fig.text(
        0.5,
        0.01,
        DISCLAIMER_TEXT,
        ha="center",
        fontsize=8,
        style="italic",
        color="#555555",
    )

    plt.tight_layout(rect=[0, 0.03, 1, 0.98])
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"[Exp 1] Saved model comparison plot to {out_path}")


def _plot_confusion_matrices(
    cms: Dict[str, np.ndarray],
    class_names: List[str],
    out_path: Path,
) -> None:
    """Plots a 2x2 grid of confusion matrices for each algorithm."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()

    for idx, (name, cm) in enumerate(cms.items()):
        ax = axes[idx]
        disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_names)
        disp.plot(cmap="Blues", values_format="d", ax=ax, colorbar=False)
        ax.set_title(name, fontsize=11, fontweight="bold")
        ax.set_xlabel("Predicted Label", fontsize=9)
        ax.set_ylabel("True Label", fontsize=9)

    fig.suptitle(
        "Experiment 1 — Multiclass Confusion Matrices by Algorithm",
        fontsize=14,
        fontweight="bold",
        y=0.99,
    )
    fig.text(
        0.5,
        0.01,
        DISCLAIMER_TEXT,
        ha="center",
        fontsize=8,
        style="italic",
        color="#555555",
    )

    plt.tight_layout(rect=[0, 0.03, 1, 0.97])
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"[Exp 1] Saved confusion matrices plot to {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Experiment 1: Crowd Prediction Comparison")
    parser.add_argument("--data", default="ml/data/crowd_data.csv")
    parser.add_argument("--results-dir", default="research/results")
    parser.add_argument("--figures-dir", default="research/figures")
    args = parser.parse_args()

    run_experiment_1(
        data_path=args.data,
        results_dir=args.results_dir,
        figures_dir=args.figures_dir,
    )
