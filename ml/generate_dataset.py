"""
SafeCampus AI — Synthetic Campus Crowd Dataset Generator
=========================================================
DISCLAIMER:
This dataset generator produces SYNTHETIC crowd density data for research,
prototyping, and academic experimentation.
It does NOT represent physical sensor measurements from any specific college campus.
All patterns are generated from domain heuristics using a deterministic random seed.

Seed: 42 (Reproducible)
"""

from __future__ import annotations

import argparse
import datetime
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd

# Fixed deterministic seed for reproducibility
RANDOM_SEED = 42

# ---------------------------------------------------------------------------
# Campus Node Category Mapping (matching data/campus_nodes.json)
# ---------------------------------------------------------------------------
LOCATION_PROFILES: Dict[int, Dict[str, any]] = {
    1:  {"name": "Main Gate",     "category": "gate",      "baseline": 0.25},
    2:  {"name": "Admin Block",   "category": "admin",     "baseline": 0.15},
    3:  {"name": "Junction A",    "category": "junction",  "baseline": 0.20},
    4:  {"name": "CSE Block",     "category": "academic",  "baseline": 0.30},
    5:  {"name": "ECE Block",     "category": "academic",  "baseline": 0.28},
    6:  {"name": "Junction B",    "category": "junction",  "baseline": 0.25},
    7:  {"name": "Library",       "category": "library",   "baseline": 0.25},
    8:  {"name": "Canteen",       "category": "canteen",   "baseline": 0.20},
    9:  {"name": "Lab A",         "category": "lab",       "baseline": 0.25},
    10: {"name": "Lab B",         "category": "lab",       "baseline": 0.25},
    11: {"name": "Auditorium",    "category": "event",     "baseline": 0.10},
    12: {"name": "Sports Ground", "category": "outdoor",   "baseline": 0.15},
    13: {"name": "Hostel A",      "category": "hostel",    "baseline": 0.30},
    14: {"name": "Hostel B",      "category": "hostel",    "baseline": 0.30},
    15: {"name": "Health Center", "category": "health",    "baseline": 0.15},
    16: {"name": "Parking Lot",   "category": "parking",   "baseline": 0.20},
    17: {"name": "Corridor C",    "category": "corridor",  "baseline": 0.35},
    18: {"name": "Junction C",    "category": "junction",  "baseline": 0.22},
    19: {"name": "Dept Office",   "category": "admin",     "baseline": 0.20},
    20: {"name": "Side Gate",     "category": "gate",      "baseline": 0.18},
}


def _compute_activity_crowd(
    loc_id: int,
    category: str,
    hour: int,
    is_weekend: bool,
    class_activity: int,
    event_flag: int,
    exam_flag: int,
    holiday_flag: int,
) -> float:
    """Calculates domain-specific crowd influence for a location at a given hour."""
    if holiday_flag:
        if category == "hostel":
            return 0.50 if (10 <= hour <= 21) else 0.25
        return 0.05

    crowd = 0.10

    if category in ("academic", "lab"):
        if not is_weekend and class_activity:
            if 9 <= hour <= 12 or 13 <= hour <= 16:
                crowd = 0.85
            elif 12 < hour < 13:
                crowd = 0.40
            else:
                crowd = 0.25
        elif exam_flag and not is_weekend:
            crowd = 0.90 if (9 <= hour <= 13 or 14 <= hour <= 17) else 0.20
        else:
            crowd = 0.12

    elif category == "canteen":
        if 12 <= hour <= 14:
            crowd = 0.95 if not is_weekend else 0.70
        elif 8 <= hour <= 9 or 16 <= hour <= 17:
            crowd = 0.78 if not is_weekend else 0.50
        elif 10 <= hour <= 11 or 15 <= hour <= 16:
            crowd = 0.45
        else:
            crowd = 0.15

    elif category == "library":
        if exam_flag:
            crowd = 0.92 if (9 <= hour <= 21) else 0.40
        elif not is_weekend:
            crowd = 0.75 if (11 <= hour <= 19) else 0.25
        else:
            crowd = 0.45 if (10 <= hour <= 17) else 0.15

    elif category in ("gate", "parking"):
        if not is_weekend:
            if 8 <= hour <= 9:
                crowd = 0.90
            elif 16 <= hour <= 18:
                crowd = 0.88
            elif 12 <= hour <= 14:
                crowd = 0.55
            else:
                crowd = 0.18
        else:
            crowd = 0.35 if (10 <= hour <= 18) else 0.10

    elif category == "event":  # Auditorium
        if event_flag:
            crowd = 0.95 if (10 <= hour <= 21) else 0.40
        else:
            crowd = 0.05

    elif category == "outdoor":  # Sports ground
        if 16 <= hour <= 19:
            crowd = 0.80
        elif 6 <= hour <= 8:
            crowd = 0.55
        else:
            crowd = 0.10

    elif category == "hostel":
        if 7 <= hour <= 9 or 19 <= hour <= 23:
            crowd = 0.85
        elif 10 <= hour <= 17:
            crowd = 0.35 if not is_weekend else 0.75
        else:
            crowd = 0.20

    elif category in ("corridor", "junction"):
        if not is_weekend and class_activity:
            crowd = 0.80 if hour in (9, 10, 12, 13, 16) else 0.50
        elif not is_weekend and (12 <= hour <= 14):
            crowd = 0.82
        else:
            crowd = 0.20

    else:  # Admin / health
        if not is_weekend and (10 <= hour <= 16):
            crowd = 0.55
        else:
            crowd = 0.12

    return crowd


def generate_crowd_dataset(
    num_days: int = 60,
    start_date: str = "2026-01-05",
    output_path: str = "ml/data/crowd_data.csv",
    seed: int = RANDOM_SEED,
) -> pd.DataFrame:
    """
    Generates synthetic campus crowd observations.

    Parameters
    ----------
    num_days   : Number of continuous simulation days.
    start_date : YYYY-MM-DD starting point (defaults to Monday 2026-01-05).
    output_path: Path to save the generated CSV.
    seed       : Pseudo-random number generator seed.

    Returns
    -------
    pd.DataFrame with all required columns.
    """
    rng = np.random.default_rng(seed)

    start_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    records: List[Dict[str, any]] = []

    # Historical moving tracking per location to generate realistic historical_crowd
    recent_history: Dict[int, float] = {
        loc_id: info["baseline"] for loc_id, info in LOCATION_PROFILES.items()
    }

    # Calendar period configuration
    exam_days = set(range(35, 46))
    fest_days = set(range(20, 23))
    holidays = {15, 26, 50}

    for day_idx in range(num_days):
        current_date = start_dt + datetime.timedelta(days=day_idx)
        date_str = current_date.strftime("%Y-%m-%d")
        day_of_week = current_date.weekday()
        is_weekend = day_of_week in (5, 6)

        holiday_flag = 1 if (day_idx in holidays or (is_weekend and rng.random() < 0.05)) else 0
        exam_flag = 1 if (day_idx in exam_days and not is_weekend) else 0
        fest_flag = 1 if (day_idx in fest_days) else 0

        for hour in range(24):
            timestamp_str = f"{date_str}T{hour:02d}:00:00"

            # Class activity
            if not is_weekend and not holiday_flag and not exam_flag and (9 <= hour <= 16):
                class_activity = 1
            else:
                class_activity = 0

            # Events
            if fest_flag and (10 <= hour <= 21):
                event_flag = 1
            elif not is_weekend and hour in (15, 16, 17) and rng.random() < 0.20:
                event_flag = 1
            else:
                event_flag = 0

            for loc_id, info in LOCATION_PROFILES.items():
                category = info["category"]
                base_val = info["baseline"]

                activity_crowd = _compute_activity_crowd(
                    loc_id=loc_id,
                    category=category,
                    hour=hour,
                    is_weekend=is_weekend,
                    class_activity=class_activity,
                    event_flag=event_flag if loc_id in (11, 12, 17) else 0,
                    exam_flag=exam_flag,
                    holiday_flag=holiday_flag,
                )

                hist_val = recent_history[loc_id]

                # Noise term
                noise = float(rng.normal(0.0, 0.03))

                # Composite crowd intensity in [0, 1]
                crowd_intensity = (
                    0.60 * activity_crowd +
                    0.30 * hist_val +
                    0.10 * base_val +
                    noise
                )
                crowd_intensity = float(np.clip(crowd_intensity, 0.02, 0.98))

                # Update running history for next hour
                recent_history[loc_id] = 0.65 * hist_val + 0.35 * crowd_intensity

                # Discretize crowd level into balanced standard research categories
                if crowd_intensity < 0.28:
                    crowd_level = "LOW"
                elif crowd_intensity < 0.52:
                    crowd_level = "MEDIUM"
                elif crowd_intensity < 0.74:
                    crowd_level = "HIGH"
                else:
                    crowd_level = "VERY_HIGH"

                records.append({
                    "timestamp": timestamp_str,
                    "date": date_str,
                    "hour": hour,
                    "day_of_week": day_of_week,
                    "location_id": loc_id,
                    "event_flag": event_flag,
                    "class_activity": class_activity,
                    "exam_flag": exam_flag,
                    "holiday_flag": holiday_flag,
                    "historical_crowd": round(hist_val, 4),
                    "crowd_level": crowd_level,
                })

    df = pd.DataFrame(records)

    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_file, index=False)

    print(f"Generated synthetic dataset with {len(df):,} records at {out_file}")
    counts = df["crowd_level"].value_counts()
    props = df["crowd_level"].value_counts(normalize=True).round(3)
    dist_df = pd.DataFrame({"count": counts, "proportion": props})
    print(f"Crowd Level Distribution:\n{dist_df}")

    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic campus crowd dataset.")
    parser.add_argument("--days", type=int, default=60, help="Number of simulation days")
    parser.add_argument("--output", type=str, default="ml/data/crowd_data.csv", help="Output CSV path")
    parser.add_argument("--seed", type=int, default=RANDOM_SEED, help="Random seed")
    args = parser.parse_args()

    generate_crowd_dataset(
        num_days=args.days,
        output_path=args.output,
        seed=args.seed,
    )
