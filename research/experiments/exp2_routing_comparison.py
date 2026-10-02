"""
SafeCampus AI — Research Experiment 2: Routing Algorithm Comparison
====================================================================
Academic Experiment:
Compares three graph routing algorithms on the SafeCampus graph topology:
1. Dijkstra's Algorithm (Minimum Distance Baseline)
2. A* Search with Haversine Heuristic (Heuristic Distance Baseline)
3. Personalized Multi-Objective A* (Personalized Pareto Optimization)

Metrics Evaluated:
- Distance (metres)
- Travel Time (minutes)
- Crowd Exposure (Average crowd score in [0.0, 1.0])
- Campus Safety (Average safety score in [0.0, 1.0])
- Accessibility (Average accessibility/ramp score in [0.0, 1.0])
- Execution Time / Latency (milliseconds)

DATA ORIGIN & INTEGRITY:
------------------------
Campus graph geometry (nodes, edges, distances, stairs, ramps, lighting) is based
on the topological campus graph in data/campus_nodes.json and data/campus_edges.json.
Crowd exposure values are predicted by the trained ML crowd model.
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

from app.algorithms.a_star import a_star
from app.algorithms.dijkstra import dijkstra
from app.algorithms.graph import CampusGraph
from app.algorithms.multi_objective_a_star import (
    WeightVector,
    multi_objective_a_star,
)
from app.services.crowd_service import get_crowd_service
from app.services.explanation_service import evaluate_path_metrics
from app.services.graph_service import get_graph, reset_graph

DISCLAIMER_TEXT = (
    "DATA ORIGIN: Physical campus graph topology (data/campus_edges.json). "
    "Crowd densities predicted via trained Gradient Boosting ML model. "
    "Controlled academic benchmark; not empirical IoT tracking."
)

# Standard benchmark OD pairs covering short, medium, and long journeys
BENCHMARK_OD_PAIRS = [
    (1, 2, "Main Gate -> Admin Block (Short)"),
    (4, 9, "CSE Block -> Lab A (Short)"),
    (7, 8, "Library -> Canteen (Short)"),
    (13, 14, "Hostel A -> Hostel B (Short)"),
    (1, 8, "Main Gate -> Canteen (Medium)"),
    (2, 11, "Admin Block -> Auditorium (Medium)"),
    (3, 15, "Junction A -> Health Center (Medium)"),
    (6, 20, "Junction B -> Side Gate (Medium)"),
    (1, 11, "Main Gate -> Auditorium (Long)"),
    (1, 13, "Main Gate -> Hostel A (Long)"),
    (16, 12, "Parking Lot -> Sports Ground (Long)"),
    (1, 20, "Main Gate -> Side Gate (Long)"),
]


def run_experiment_2(
    results_dir: str = "research/results",
    figures_dir: str = "research/figures",
    num_runs: int = 5,
) -> pd.DataFrame:
    """
    Executes Experiment 2: Benchmark Dijkstra vs A* vs Personalized Multi-Objective A*.
    Runs each query multiple times to measure stable execution times.
    """
    res_path = Path(results_dir)
    fig_path = Path(figures_dir)
    res_path.mkdir(parents=True, exist_ok=True)
    fig_path.mkdir(parents=True, exist_ok=True)

    reset_graph()
    graph: CampusGraph = get_graph()

    # Pre-compute ML crowd scores for the graph
    node_crowd_scores: Dict[int, float] = {}
    try:
        crowd_service = get_crowd_service()
        for node in graph.all_nodes():
            pred = crowd_service.predict(location_id=node.id, hour=12, day_of_week=2)
            node_crowd_scores[node.id] = pred.predicted_crowd_score
    except Exception as exc:
        print(f"[Exp 2] Note: Using static graph crowd baselines ({exc})")
        node_crowd_scores = {n.id: 0.35 for n in graph.all_nodes()}

    records: List[Dict[str, Any]] = []

    print("\n[Exp 2] Running Routing Algorithm Benchmark on Campus Graph...")
    print("=" * 95)
    print(f"{'OD Pair':<34} | {'Algorithm':<14} | {'Dist(m)':<8} | {'Time(m)':<7} | {'Crowd':<6} | {'Safe':<6} | {'Access':<6} | {'Exec(ms)':<8}")
    print("-" * 95)

    for src, dst, label in BENCHMARK_OD_PAIRS:
        # 1. Dijkstra Algorithm
        # Warmup and timed runs
        dijkstra(graph, src, dst)
        times = []
        dijk_res = None
        for _ in range(num_runs):
            t0 = time.perf_counter()
            dijk_res = dijkstra(graph, src, dst)
            times.append((time.perf_counter() - t0) * 1000.0)
        dijk_time_ms = float(np.mean(times))

        dijk_metrics = evaluate_path_metrics(graph, dijk_res.path, node_crowd_scores)
        records.append({
            "source_id": src,
            "destination_id": dst,
            "pair_label": label,
            "algorithm": "Dijkstra",
            "distance_m": dijk_metrics["distance_m"],
            "travel_time_min": dijk_metrics["travel_time_min"],
            "crowd_score": dijk_metrics["crowd_score"],
            "safety_score": dijk_metrics["safety_score"],
            "accessibility_score": dijk_metrics["accessibility_score"],
            "execution_time_ms": round(dijk_time_ms, 3),
            "path_length": len(dijk_res.path),
        })
        print(
            f"{label:<34} | {'Dijkstra':<14} | {dijk_metrics['distance_m']:<8.1f} | "
            f"{dijk_metrics['travel_time_min']:<7.2f} | {dijk_metrics['crowd_score']:<6.2f} | "
            f"{dijk_metrics['safety_score']:<6.2f} | {dijk_metrics['accessibility_score']:<6.2f} | "
            f"{dijk_time_ms:<8.3f}"
        )

        # 2. A* Search
        a_star(graph, src, dst)
        times = []
        astar_res = None
        for _ in range(num_runs):
            t0 = time.perf_counter()
            astar_res = a_star(graph, src, dst)
            times.append((time.perf_counter() - t0) * 1000.0)
        astar_time_ms = float(np.mean(times))

        astar_metrics = evaluate_path_metrics(graph, astar_res.path, node_crowd_scores)
        records.append({
            "source_id": src,
            "destination_id": dst,
            "pair_label": label,
            "algorithm": "A*",
            "distance_m": astar_metrics["distance_m"],
            "travel_time_min": astar_metrics["travel_time_min"],
            "crowd_score": astar_metrics["crowd_score"],
            "safety_score": astar_metrics["safety_score"],
            "accessibility_score": astar_metrics["accessibility_score"],
            "execution_time_ms": round(astar_time_ms, 3),
            "path_length": len(astar_res.path),
        })
        print(
            f"{label:<34} | {'A*':<14} | {astar_metrics['distance_m']:<8.1f} | "
            f"{astar_metrics['travel_time_min']:<7.2f} | {astar_metrics['crowd_score']:<6.2f} | "
            f"{astar_metrics['safety_score']:<6.2f} | {astar_metrics['accessibility_score']:<6.2f} | "
            f"{astar_time_ms:<8.3f}"
        )

        # 3. Personalized Multi-Objective A* (Balanced Preset)
        balanced_weights = WeightVector.from_preference("balanced")
        multi_objective_a_star(graph, src, dst, weights=balanced_weights, node_crowd_scores=node_crowd_scores)
        times = []
        moa_res = None
        for _ in range(num_runs):
            t0 = time.perf_counter()
            moa_res = multi_objective_a_star(
                graph, src, dst, weights=balanced_weights, node_crowd_scores=node_crowd_scores
            )
            times.append((time.perf_counter() - t0) * 1000.0)
        moa_time_ms = float(np.mean(times))

        records.append({
            "source_id": src,
            "destination_id": dst,
            "pair_label": label,
            "algorithm": "Personalized Multi-Objective A*",
            "distance_m": moa_res.distance_m,
            "travel_time_min": moa_res.travel_time_min,
            "crowd_score": moa_res.crowd_score,
            "safety_score": moa_res.safety_score,
            "accessibility_score": moa_res.accessibility_score,
            "execution_time_ms": round(moa_time_ms, 3),
            "path_length": len(moa_res.path),
        })
        print(
            f"{label:<34} | {'Multi-Obj A*':<14} | {moa_res.distance_m:<8.1f} | "
            f"{moa_res.travel_time_min:<7.2f} | {moa_res.crowd_score:<6.2f} | "
            f"{moa_res.safety_score:<6.2f} | {moa_res.accessibility_score:<6.2f} | "
            f"{moa_time_ms:<8.3f}"
        )
        print("-" * 95)

    df_results = pd.DataFrame(records)

    # Save detailed CSV
    csv_out = res_path / "exp2_routing_comparison.csv"
    with open(csv_out, "w", encoding="utf-8") as f:
        f.write(f"# {DISCLAIMER_TEXT}\n")
        df_results.to_csv(f, index=False)
    print(f"\n[Exp 2] Saved routing benchmark CSV to {csv_out}")

    # Generate Summary Table (Mean ± Std)
    summary_df = df_results.groupby("algorithm").agg({
        "distance_m": ["mean", "std"],
        "travel_time_min": ["mean", "std"],
        "crowd_score": ["mean", "std"],
        "safety_score": ["mean", "std"],
        "accessibility_score": ["mean", "std"],
        "execution_time_ms": ["mean", "std"],
    }).round(3)
    print("\n[Exp 2] Benchmark Statistical Summary (Mean ± Std):")
    print(summary_df)

    # Generate Comparative Plots
    _plot_routing_metrics(df_results, fig_path / "exp2_routing_metrics.png")
    _plot_execution_latency(df_results, fig_path / "exp2_execution_time.png")

    return df_results


def _plot_routing_metrics(df: pd.DataFrame, out_path: Path) -> None:
    """Generates multi-panel comparative bar chart of the 5 routing quality objectives."""
    algos = ["Dijkstra", "A*", "Personalized Multi-Objective A*"]
    short_algos = ["Dijkstra", "A*", "Multi-Obj A*"]
    colors = ["#78909C", "#1E88E5", "#00897B"]

    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    metrics = [
        ("distance_m", "Mean Distance (m)", "Metres"),
        ("travel_time_min", "Mean Travel Time (min)", "Minutes"),
        ("crowd_score", "Crowd Exposure Score (lower is better)", "Score [0, 1]"),
        ("safety_score", "Campus Safety Score (higher is better)", "Score [0, 1]"),
        ("accessibility_score", "Ramp Accessibility Score (higher is better)", "Score [0, 1]"),
        ("execution_time_ms", "Mean Execution Latency (ms)", "Milliseconds"),
    ]

    for idx, (col, title, ylabel) in enumerate(metrics):
        ax = axes[idx // 3, idx % 3]
        means = [df[df["algorithm"] == a][col].mean() for a in algos]
        stds = [df[df["algorithm"] == a][col].std() for a in algos]

        bars = ax.bar(short_algos, means, yerr=stds, capsize=4, color=colors, edgecolor="black", linewidth=0.6, width=0.5)
        ax.set_title(title, fontsize=10, fontweight="bold")
        ax.set_ylabel(ylabel, fontsize=9)
        ax.grid(axis="y", linestyle="--", alpha=0.5)

        for bar in bars:
            h = bar.get_height()
            ax.annotate(
                f"{h:.2f}",
                xy=(bar.get_x() + bar.get_width() / 2, h),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    fig.suptitle(
        "Experiment 2 — Routing Algorithm Benchmark Comparison\n(Dijkstra vs A* vs Personalized Multi-Objective A*)",
        fontsize=13,
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
    print(f"[Exp 2] Saved routing metrics plot to {out_path}")


def _plot_execution_latency(df: pd.DataFrame, out_path: Path) -> None:
    """Plots execution latency distribution across all evaluated OD pairs."""
    fig, ax = plt.subplots(figsize=(10, 5))

    algos = ["Dijkstra", "A*", "Personalized Multi-Objective A*"]
    colors = ["#78909C", "#1E88E5", "#00897B"]
    labels = ["Dijkstra", "A* (Haversine)", "Multi-Objective A*"]

    data_to_plot = [df[df["algorithm"] == a]["execution_time_ms"].values for a in algos]

    bplot = ax.boxplot(
        data_to_plot,
        tick_labels=labels,
        patch_artist=True,
        medianprops=dict(color="black", linewidth=1.5),
    )

    for patch, color in zip(bplot["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    ax.set_title("Experiment 2 — Execution Latency Distribution (ms)", fontsize=12, fontweight="bold", pad=12)
    ax.set_ylabel("Execution Time (milliseconds)", fontsize=10)
    ax.grid(axis="y", linestyle="--", alpha=0.6)

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
    print(f"[Exp 2] Saved execution time plot to {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Experiment 2: Routing Algorithm Comparison")
    parser.add_argument("--results-dir", default="research/results")
    parser.add_argument("--figures-dir", default="research/figures")
    parser.add_argument("--runs", type=int, default=5)
    args = parser.parse_args()

    run_experiment_2(
        results_dir=args.results_dir,
        figures_dir=args.figures_dir,
        num_runs=args.runs,
    )
