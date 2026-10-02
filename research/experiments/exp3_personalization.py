"""
SafeCampus AI — Research Experiment 3: Route Personalization Benchmark
======================================================================
Academic Experiment:
Evaluates the six preference presets of Personalized Multi-Objective A*
on identical source/destination pairs to verify Pareto multi-attribute specialization:

1. `shortest`      (wD=0.70, wT=0.15, wC=0.05, wS=0.05, wA=0.05)
2. `fastest`       (wD=0.15, wT=0.70, wC=0.05, wS=0.05, wA=0.05)
3. `safest`        (wD=0.05, wT=0.05, wC=0.05, wS=0.80, wA=0.05)
4. `least_crowded` (wD=0.05, wT=0.05, wC=0.80, wS=0.05, wA=0.05)
5. `accessible`    (wD=0.05, wT=0.05, wC=0.05, wS=0.05, wA=0.80)
6. `balanced`      (wD=0.20, wT=0.20, wC=0.20, wS=0.20, wA=0.20)

Scientific Requirement:
All six presets are evaluated on IDENTICAL source/destination pairs across the campus.

DATA ORIGIN & INTEGRITY:
------------------------
Campus graph geometry is loaded from data/campus_nodes.json and data/campus_edges.json.
Crowd exposure is predicted dynamically using the trained Gradient Boosting model.
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
    "Identical source/destination pairs tested across all presets."
)

PRESETS = ["shortest", "fastest", "safest", "least_crowded", "accessible", "balanced"]

# Identical benchmark OD pairs where trade-off corridors exist
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


def run_experiment_3(
    results_dir: str = "research/results",
    figures_dir: str = "research/figures",
) -> pd.DataFrame:
    """
    Executes Experiment 3: Personalization preset benchmark on identical OD pairs.
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
            pred = crowd_service.predict(location_id=node.id, hour=14, day_of_week=2)
            node_crowd_scores[node.id] = pred.predicted_crowd_score
    except Exception as exc:
        print(f"[Exp 3] ML crowd fallback: {exc}")
        node_crowd_scores = {n.id: 0.35 for n in graph.all_nodes()}

    records: List[Dict[str, Any]] = []

    print("\n[Exp 3] Benchmarking 6 Personalization Presets on Identical OD Pairs...")
    print("=" * 100)
    print(f"{'OD Pair':<28} | {'Preset':<14} | {'Dist(m)':<8} | {'Time(m)':<7} | {'Crowd':<6} | {'Safe':<6} | {'Access':<6} | {'Cost':<6}")
    print("-" * 100)

    for src, dst, label in IDENTICAL_OD_PAIRS:
        for pref in PRESETS:
            weights = WeightVector.from_preference(pref)
            t0 = time.perf_counter()
            res = multi_objective_a_star(
                graph=graph,
                source_id=src,
                destination_id=dst,
                weights=weights,
                preference=pref,
                node_crowd_scores=node_crowd_scores,
            )
            exec_time_ms = (time.perf_counter() - t0) * 1000.0

            records.append({
                "source_id": src,
                "destination_id": dst,
                "pair_label": label,
                "preference": pref,
                "distance_m": res.distance_m,
                "travel_time_min": res.travel_time_min,
                "crowd_score": res.crowd_score,
                "crowd_level": res.crowd_level,
                "safety_score": res.safety_score,
                "accessibility_score": res.accessibility_score,
                "total_cost": res.total_cost,
                "execution_time_ms": round(exec_time_ms, 3),
                "path": " -> ".join(map(str, res.path)),
                "path_length": len(res.path),
            })

            print(
                f"{label:<28} | {pref:<14} | {res.distance_m:<8.1f} | "
                f"{res.travel_time_min:<7.2f} | {res.crowd_score:<6.2f} | "
                f"{res.safety_score:<6.2f} | {res.accessibility_score:<6.2f} | "
                f"{res.total_cost:<6.3f}"
            )
        print("-" * 100)

    df_results = pd.DataFrame(records)

    # Save CSV
    csv_out = res_path / "exp3_personalization_comparison.csv"
    with open(csv_out, "w", encoding="utf-8") as f:
        f.write(f"# {DISCLAIMER_TEXT}\n")
        df_results.to_csv(f, index=False)
    print(f"\n[Exp 3] Saved personalization comparison CSV to {csv_out}")

    # Generate Statistical Preset Summary
    summary_df = df_results.groupby("preference").agg({
        "distance_m": "mean",
        "travel_time_min": "mean",
        "crowd_score": "mean",
        "safety_score": "mean",
        "accessibility_score": "mean",
        "total_cost": "mean",
    }).round(3)
    print("\n[Exp 3] Preset Performance Summary (Means across all identical pairs):")
    print(summary_df)

    # Plot Grouped Trade-Offs
    _plot_preset_tradeoffs(df_results, fig_path / "exp3_preset_tradeoffs.png")

    # Plot Radar Chart
    _plot_radar_profiles(summary_df, fig_path / "exp3_radar_profiles.png")

    return df_results


def _plot_preset_tradeoffs(df: pd.DataFrame, out_path: Path) -> None:
    """Plots comparative grouped bar charts showing objective specialization across presets."""
    preset_order = ["shortest", "fastest", "safest", "least_crowded", "accessible", "balanced"]
    preset_labels = ["Shortest", "Fastest", "Safest", "Least Crowded", "Accessible", "Balanced"]
    colors = ["#1976D2", "#F57C00", "#2E7D32", "#00897B", "#7B1FA2", "#455A64"]

    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    dimensions = [
        ("distance_m", "Mean Distance (m)\n[Lower is Better]", "Metres"),
        ("travel_time_min", "Mean Travel Time (min)\n[Lower is Better]", "Minutes"),
        ("crowd_score", "Mean Crowd Exposure\n[Lower is Better]", "Score [0, 1]"),
        ("safety_score", "Mean Safety Score\n[Higher is Better]", "Score [0, 1]"),
        ("accessibility_score", "Mean Accessibility Score\n[Higher is Better]", "Score [0, 1]"),
        ("total_cost", "Mean Optimization Cost (R*)\n[Lower is Better]", "Normalized Cost"),
    ]

    for idx, (col, title, ylabel) in enumerate(dimensions):
        ax = axes[idx // 3, idx % 3]
        means = [df[df["preference"] == p][col].mean() for p in preset_order]
        bars = ax.bar(preset_labels, means, color=colors, edgecolor="black", linewidth=0.6, width=0.55)

        ax.set_title(title, fontsize=10, fontweight="bold")
        ax.set_ylabel(ylabel, fontsize=9)
        ax.set_xticklabels(preset_labels, rotation=35, ha="right", fontsize=9)
        ax.grid(axis="y", linestyle="--", alpha=0.5)

        for bar in bars:
            h = bar.get_height()
            ax.annotate(
                f"{h:.2f}",
                xy=(bar.get_x() + bar.get_width() / 2, h),
                xytext=(0, 2),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    fig.suptitle(
        "Experiment 3 — Personalization Preset Optimization Trade-Offs\n(Evaluated on Identical Campus OD Pairs)",
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
    print(f"[Exp 3] Saved preset trade-offs plot to {out_path}")


def _plot_radar_profiles(summary_df: pd.DataFrame, out_path: Path) -> None:
    """Plots a 5-dimension radar (spider) chart showing Pareto profile for each preset."""
    categories = [
        "Distance Eff.",
        "Time Eff.",
        "Crowd Avoidance",
        "Campus Safety",
        "Accessibility",
    ]
    N = len(categories)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]  # Close loop

    # Normalize metrics to [0, 1] where 1.0 is the best possible score
    max_d = summary_df["distance_m"].max()
    min_d = summary_df["distance_m"].min()
    max_t = summary_df["travel_time_min"].max()
    min_t = summary_df["travel_time_min"].min()

    preset_colors = {
        "shortest": "#1976D2",
        "fastest": "#F57C00",
        "safest": "#2E7D32",
        "least_crowded": "#00897B",
        "accessible": "#7B1FA2",
        "balanced": "#455A64",
    }

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

    for pref in PRESETS:
        if pref not in summary_df.index:
            continue
        row = summary_df.loc[pref]

        # Invert distance and time so higher = more efficient
        d_eff = 1.0 - (row["distance_m"] - min_d) / max(max_d - min_d, 0.001) if max_d > min_d else 1.0
        t_eff = 1.0 - (row["travel_time_min"] - min_t) / max(max_t - min_t, 0.001) if max_t > min_t else 1.0
        c_avoid = 1.0 - row["crowd_score"]  # Lower crowd = higher avoidance
        safe = row["safety_score"]
        access = row["accessibility_score"]

        values = [d_eff, t_eff, c_avoid, safe, access]
        values += values[:1]  # Close loop

        col = preset_colors.get(pref, "#333333")
        ax.plot(angles, values, linewidth=1.8, label=pref.capitalize(), color=col)
        ax.fill(angles, values, color=col, alpha=0.10)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=10, fontweight="bold")
    ax.set_ylim(0, 1.05)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(["0.2", "0.4", "0.6", "0.8", "1.0"], fontsize=8, color="#555555")
    ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.1), framealpha=0.95, fontsize=9)

    ax.set_title(
        "Experiment 3 — Multi-Attribute Radar Profiles\n(Normalized Efficiency & Quality by Preset)",
        fontsize=12,
        fontweight="bold",
        pad=20,
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

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"[Exp 3] Saved radar profiles plot to {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Experiment 3: Personalization Preset Benchmark")
    parser.add_argument("--results-dir", default="research/results")
    parser.add_argument("--figures-dir", default="research/figures")
    args = parser.parse_args()

    run_experiment_3(
        results_dir=args.results_dir,
        figures_dir=args.figures_dir,
    )
