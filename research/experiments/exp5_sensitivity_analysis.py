"""
SafeCampus AI — Research Experiment 5: Weight Sensitivity Analysis
===================================================================
Academic Experiment:
Systematically varies each multi-objective weight w_i in [0.10, 0.90] to evaluate
the elasticity and stability of route characteristics:

1. Distance Weight Sweep:      wD in [0.10, 0.90], others = (1 - wD)/4
2. Time Weight Sweep:          wT in [0.10, 0.90], others = (1 - wT)/4
3. Crowd Weight Sweep:         wC in [0.10, 0.90], others = (1 - wC)/4
4. Safety Weight Sweep:        wS in [0.10, 0.90], others = (1 - wS)/4
5. Accessibility Weight Sweep: wA in [0.10, 0.90], others = (1 - wA)/4

Constraint: Sum of weights equals 1.00 at every step.

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
    "Controlled parameter sweep across [0.10, 0.90] with sum(weights) = 1.00."
)

WEIGHT_STEPS = [0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90]

BENCHMARK_PAIRS = [
    (1, 8, "Main Gate -> Canteen"),
    (1, 11, "Main Gate -> Auditorium"),
    (1, 13, "Main Gate -> Hostel A"),
    (1, 20, "Main Gate -> Side Gate"),
    (4, 11, "CSE Block -> Auditorium"),
    (6, 13, "Junction B -> Hostel A"),
    (16, 12, "Parking Lot -> Sports Ground"),
]


def _build_sweep_weight(swept_dim: str, value: float) -> WeightVector:
    """Builds a normalized WeightVector where swept_dim = value, and others share (1 - value)/4."""
    rem = round((1.0 - value) / 4.0, 6)
    weights = {
        "wD": rem,
        "wT": rem,
        "wC": rem,
        "wS": rem,
        "wA": rem,
    }
    weights[swept_dim] = round(value, 6)

    # Correct rounding residuals so sum is exactly 1.00
    total = sum(weights.values())
    diff = round(1.0 - total, 6)
    if diff != 0.0:
        first_other = [k for k in weights if k != swept_dim][0]
        weights[first_other] = round(weights[first_other] + diff, 6)

    return WeightVector(**weights)


def run_experiment_5(
    results_dir: str = "research/results",
    figures_dir: str = "research/figures",
) -> pd.DataFrame:
    """
    Executes Experiment 5: Systematically sweeps each of the 5 objective weights in [0.1, 0.9].
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
        print(f"[Exp 5] ML crowd fallback: {exc}")
        node_crowd_scores = {n.id: 0.35 for n in graph.all_nodes()}

    sweep_dims = [
        ("wD", "Distance Weight (wD)"),
        ("wT", "Time Weight (wT)"),
        ("wC", "Crowd Weight (wC)"),
        ("wS", "Safety Weight (wS)"),
        ("wA", "Accessibility Weight (wA)"),
    ]

    records: List[Dict[str, Any]] = []

    print("\n[Exp 5] Executing 5-Dimensional Weight Sensitivity Sweep [0.10 -> 0.90]...")
    print("=" * 95)
    print(f"{'Swept Dimension':<26} | {'Weight':<8} | {'Dist(m)':<8} | {'Time(m)':<7} | {'Crowd':<6} | {'Safe':<6} | {'Access':<6}")
    print("-" * 95)

    for dim_key, dim_name in sweep_dims:
        for val in WEIGHT_STEPS:
            wv = _build_sweep_weight(dim_key, val)

            dist_list = []
            time_list = []
            crowd_list = []
            safe_list = []
            access_list = []
            cost_list = []

            for src, dst, _ in BENCHMARK_PAIRS:
                res = multi_objective_a_star(
                    graph=graph,
                    source_id=src,
                    destination_id=dst,
                    weights=wv,
                    preference="custom",
                    node_crowd_scores=node_crowd_scores,
                )
                dist_list.append(res.distance_m)
                time_list.append(res.travel_time_min)
                crowd_list.append(res.crowd_score)
                safe_list.append(res.safety_score)
                access_list.append(res.accessibility_score)
                cost_list.append(res.total_cost)

            mean_dist = round(float(np.mean(dist_list)), 2)
            mean_time = round(float(np.mean(time_list)), 3)
            mean_crowd = round(float(np.mean(crowd_list)), 3)
            mean_safe = round(float(np.mean(safe_list)), 3)
            mean_access = round(float(np.mean(access_list)), 3)
            mean_cost = round(float(np.mean(cost_list)), 4)

            records.append({
                "dimension": dim_key,
                "dimension_name": dim_name,
                "weight_value": val,
                "mean_distance_m": mean_dist,
                "mean_travel_time_min": mean_time,
                "mean_crowd_score": mean_crowd,
                "mean_safety_score": mean_safe,
                "mean_accessibility_score": mean_access,
                "mean_total_cost": mean_cost,
            })

            print(
                f"{dim_name:<26} | {val:<8.2f} | {mean_dist:<8.1f} | "
                f"{mean_time:<7.2f} | {mean_crowd:<6.3f} | "
                f"{mean_safe:<6.3f} | {mean_access:<6.3f}"
            )
        print("-" * 95)

    df_results = pd.DataFrame(records)

    # Save CSV
    csv_out = res_path / "exp5_sensitivity_analysis.csv"
    with open(csv_out, "w", encoding="utf-8") as f:
        f.write(f"# {DISCLAIMER_TEXT}\n")
        df_results.to_csv(f, index=False)
    print(f"\n[Exp 5] Saved sensitivity analysis CSV to {csv_out}")

    # Plot Sensitivity Curves
    _plot_sensitivity_curves(df_results, fig_path / "exp5_sensitivity_curves.png")

    return df_results


def _plot_sensitivity_curves(df: pd.DataFrame, out_path: Path) -> None:
    """Plots 5 subplots showing how route metrics respond as each weight sweeps [0.10, 0.90]."""
    fig, axes = plt.subplots(2, 3, figsize=(16, 9))

    sweep_configs = [
        ("wD", "Distance Weight (wD) Sweep", "mean_distance_m", "Mean Distance (m)", "#1976D2", "lower"),
        ("wT", "Time Weight (wT) Sweep", "mean_travel_time_min", "Mean Travel Time (min)", "#F57C00", "lower"),
        ("wC", "Crowd Avoidance Weight (wC) Sweep", "mean_crowd_score", "Mean Crowd Exposure", "#00897B", "lower"),
        ("wS", "Safety Weight (wS) Sweep", "mean_safety_score", "Mean Safety Score", "#2E7D32", "higher"),
        ("wA", "Accessibility Weight (wA) Sweep", "mean_accessibility_score", "Mean Accessibility Score", "#7B1FA2", "higher"),
    ]

    for idx, (dim, title, metric_col, ylabel, color, best_dir) in enumerate(sweep_configs):
        ax = axes[idx // 3, idx % 3]
        sub = df[df["dimension"] == dim]

        weights = sub["weight_value"].tolist()
        vals = sub[metric_col].tolist()

        ax.plot(weights, vals, marker="s", linewidth=2.4, markersize=6, color=color, label=f"Response ({best_dir} is better)")
        ax.fill_between(weights, vals, color=color, alpha=0.12)

        ax.set_title(title, fontsize=10, fontweight="bold")
        ax.set_xlabel(f"Weight value ({dim})", fontsize=9)
        ax.set_ylabel(ylabel, fontsize=9)
        ax.set_xticks(WEIGHT_STEPS)
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend(fontsize=8, loc="best")

    # Leave 6th subplot for combined elastic summary
    ax_last = axes[1, 2]
    for dim, _, metric_col, _, color, _ in sweep_configs:
        sub = df[df["dimension"] == dim]
        # Normalize response curve to [0, 1]
        v = sub[metric_col].values
        norm_v = (v - v.min()) / max(v.max() - v.min(), 0.001)
        ax_last.plot(sub["weight_value"].values, norm_v, label=dim, color=color, linewidth=2.0)
    ax_last.set_title("Combined Normalized Elasticity", fontsize=10, fontweight="bold")
    ax_last.set_xlabel("Weight value", fontsize=9)
    ax_last.set_ylabel("Normalized Response [0, 1]", fontsize=9)
    ax_last.grid(True, linestyle="--", alpha=0.5)
    ax_last.legend(fontsize=8, loc="best")

    fig.suptitle(
        "Experiment 5 — Objective Weight Sensitivity Analysis\n(Parameter sweep w_i in [0.10, 0.90] with sum(weights) = 1.00)",
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
    print(f"[Exp 5] Saved sensitivity curves plot to {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Experiment 5: Weight Sensitivity Analysis")
    parser.add_argument("--results-dir", default="research/results")
    parser.add_argument("--figures-dir", default="research/figures")
    args = parser.parse_args()

    run_experiment_5(
        results_dir=args.results_dir,
        figures_dir=args.figures_dir,
    )
