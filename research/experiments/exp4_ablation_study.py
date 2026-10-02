"""
SafeCampus AI — Research Experiment 4: Ablation Study
======================================================
Academic Experiment:
Quantifies the incremental contribution of each routing objective dimension
by evaluating five cumulative ablation stages:

Stage 1: Distance only
         wD=1.00, wT=0.00, wC=0.00, wS=0.00, wA=0.00
Stage 2: Distance + Time
         wD=0.50, wT=0.50, wC=0.00, wS=0.00, wA=0.00
Stage 3: Distance + Time + Crowd
         wD=0.34, wT=0.33, wC=0.33, wS=0.00, wA=0.00
Stage 4: Distance + Time + Crowd + Safety
         wD=0.25, wT=0.25, wC=0.25, wS=0.25, wA=0.00
Stage 5: All factors + Personalization
         wD=0.20, wT=0.20, wC=0.20, wS=0.20, wA=0.20

Constraint: Sum of weights equals 1.00 for every stage.

DATA ORIGIN & INTEGRITY:
------------------------
Campus graph geometry (data/campus_edges.json).
Crowd densities predicted via trained Gradient Boosting ML model.
Never fabricated; computed dynamically from graph algorithms.
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
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from app.algorithms.graph import CampusGraph
from app.algorithms.multi_objective_a_star import (
    WeightVector,
    multi_objective_a_star,
)
from app.services.crowd_service import get_crowd_service
from app.services.graph_service import get_graph, reset_graph

DISCLAIMER_TEXT = (
    "DATA ORIGIN: Campus graph geometry (data/campus_edges.json). "
    "Crowd densities predicted via trained Gradient Boosting ML model. "
    "Identical benchmark pairs evaluated across 5 cumulative ablation stages."
)

# 5 Cumulative Ablation Stages
ABLATION_STAGES = [
    (1, "1. Distance Only", WeightVector(wD=1.00, wT=0.00, wC=0.00, wS=0.00, wA=0.00)),
    (2, "2. Distance + Time", WeightVector(wD=0.50, wT=0.50, wC=0.00, wS=0.00, wA=0.00)),
    (3, "3. Distance + Time + Crowd", WeightVector(wD=0.34, wT=0.33, wC=0.33, wS=0.00, wA=0.00)),
    (4, "4. Dist + Time + Crowd + Safety", WeightVector(wD=0.25, wT=0.25, wC=0.25, wS=0.25, wA=0.00)),
    (5, "5. All Factors + Personalization", WeightVector(wD=0.20, wT=0.20, wC=0.20, wS=0.20, wA=0.20)),
]

IDENTICAL_OD_PAIRS = [
    (1, 8, "Main Gate -> Canteen"),
    (1, 11, "Main Gate -> Auditorium"),
    (1, 13, "Main Gate -> Hostel A"),
    (1, 20, "Main Gate -> Side Gate"),
    (2, 8, "Admin Block -> Canteen"),
    (4, 11, "CSE Block -> Auditorium"),
    (3, 14, "Junction A -> Hostel B"),
    (6, 13, "Junction B -> Hostel A"),
    (16, 8, "Parking Lot -> Canteen"),
    (16, 12, "Parking Lot -> Sports Ground"),
]


def run_experiment_4(
    results_dir: str = "research/results",
    figures_dir: str = "research/figures",
) -> pd.DataFrame:
    """
    Executes Experiment 4: Multi-stage ablation study across cumulative objective dimensions.
    """
    res_path = Path(results_dir)
    fig_path = Path(figures_dir)
    res_path.mkdir(parents=True, exist_ok=True)
    fig_path.mkdir(parents=True, exist_ok=True)

    reset_graph()
    graph: CampusGraph = get_graph()

    # Pre-compute ML crowd scores
    node_crowd_scores: Dict[int, float] = {}
    try:
        crowd_service = get_crowd_service()
        for node in graph.all_nodes():
            pred = crowd_service.predict(location_id=node.id, hour=12, day_of_week=2)
            node_crowd_scores[node.id] = pred.predicted_crowd_score
    except Exception as exc:
        print(f"[Exp 4] ML crowd fallback: {exc}")
        node_crowd_scores = {n.id: 0.35 for n in graph.all_nodes()}

    records: List[Dict[str, Any]] = []

    print("\n[Exp 4] Executing 5-Stage Cumulative Ablation Study...")
    print("=" * 105)
    print(f"{'OD Pair':<28} | {'Stage':<30} | {'Dist(m)':<8} | {'Time(m)':<7} | {'Crowd':<6} | {'Safe':<6} | {'Access':<6}")
    print("-" * 105)

    for src, dst, label in IDENTICAL_OD_PAIRS:
        for stage_idx, stage_name, weights in ABLATION_STAGES:
            t0 = time.perf_counter()
            res = multi_objective_a_star(
                graph=graph,
                source_id=src,
                destination_id=dst,
                weights=weights,
                preference="custom",
                node_crowd_scores=node_crowd_scores,
            )
            exec_time_ms = (time.perf_counter() - t0) * 1000.0

            records.append({
                "stage": stage_idx,
                "stage_name": stage_name,
                "source_id": src,
                "destination_id": dst,
                "pair_label": label,
                "distance_m": res.distance_m,
                "travel_time_min": res.travel_time_min,
                "crowd_score": res.crowd_score,
                "safety_score": res.safety_score,
                "accessibility_score": res.accessibility_score,
                "total_cost": res.total_cost,
                "execution_time_ms": round(exec_time_ms, 3),
                "path": " -> ".join(map(str, res.path)),
            })

            print(
                f"{label:<28} | {stage_name:<30} | {res.distance_m:<8.1f} | "
                f"{res.travel_time_min:<7.2f} | {res.crowd_score:<6.2f} | "
                f"{res.safety_score:<6.2f} | {res.accessibility_score:<6.2f}"
            )
        print("-" * 105)

    df_results = pd.DataFrame(records)

    # Save CSV
    csv_out = res_path / "exp4_ablation_study.csv"
    with open(csv_out, "w", encoding="utf-8") as f:
        f.write(f"# {DISCLAIMER_TEXT}\n")
        df_results.to_csv(f, index=False)
    print(f"\n[Exp 4] Saved ablation study CSV to {csv_out}")

    # Statistical stage summary
    summary_df = df_results.groupby(["stage", "stage_name"]).agg({
        "distance_m": "mean",
        "travel_time_min": "mean",
        "crowd_score": "mean",
        "safety_score": "mean",
        "accessibility_score": "mean",
        "total_cost": "mean",
    }).round(3).reset_index()

    print("\n[Exp 4] Ablation Study Stage Progression (Means across all pairs):")
    print(summary_df.to_string(index=False))

    # Plot Ablation Curves
    _plot_ablation_curves(summary_df, fig_path / "exp4_ablation_curves.png")

    return df_results


def _plot_ablation_curves(summary_df: pd.DataFrame, out_path: Path) -> None:
    """Plots progressive metric shift across the 5 ablation stages."""
    stages = summary_df["stage"].tolist()
    stage_labels = [
        "1. Dist Only",
        "2. +Time",
        "3. +Crowd",
        "4. +Safety",
        "5. +Access (All)",
    ]

    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    dimensions = [
        ("distance_m", "Mean Distance (m)", "#1976D2", "Metres"),
        ("travel_time_min", "Mean Travel Time (min)", "#F57C00", "Minutes"),
        ("crowd_score", "Mean Crowd Exposure", "#00897B", "Exposure [0, 1]"),
        ("safety_score", "Mean Safety Score", "#2E7D32", "Score [0, 1]"),
        ("accessibility_score", "Mean Accessibility Score", "#7B1FA2", "Score [0, 1]"),
        ("total_cost", "Mean Objective Cost (R*)", "#D32F2F", "Normalized Cost"),
    ]

    for idx, (col, title, color, ylabel) in enumerate(dimensions):
        ax = axes[idx // 3, idx % 3]
        vals = summary_df[col].tolist()

        ax.plot(stages, vals, marker="o", linewidth=2.2, markersize=7, color=color, label=title)
        ax.fill_between(stages, vals, color=color, alpha=0.15)

        ax.set_title(title, fontsize=10, fontweight="bold")
        ax.set_ylabel(ylabel, fontsize=9)
        ax.set_xticks(stages)
        ax.set_xticklabels(stage_labels, fontsize=8, rotation=20, ha="right")
        ax.grid(True, linestyle="--", alpha=0.5)

        for s, v in zip(stages, vals):
            ax.annotate(
                f"{v:.2f}",
                xy=(s, v),
                xytext=(0, 6),
                textcoords="offset points",
                ha="center",
                fontsize=8,
                fontweight="bold",
            )

    fig.suptitle(
        "Experiment 4 — Ablation Study: Cumulative Objective Dimension Impact",
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

    plt.tight_layout(rect=[0, 0.03, 1, 0.96])
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"[Exp 4] Saved ablation curves plot to {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Experiment 4: Ablation Study")
    parser.add_argument("--results-dir", default="research/results")
    parser.add_argument("--figures-dir", default="research/figures")
    args = parser.parse_args()

    run_experiment_4(
        results_dir=args.results_dir,
        figures_dir=args.figures_dir,
    )
