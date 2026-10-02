# SafeCampus AI — ML Data Directory

This directory will contain:

- `crowd_data.csv` — Synthetic crowd dataset (generated in Phase 2)
- `campus_sensor_data.csv` — Optional real sensor data (if collected)

## Dataset Schema (Phase 2)

| Column | Type | Description |
|--------|------|-------------|
| timestamp | datetime | Record timestamp |
| date | date | Date of observation |
| hour | int | Hour of day (0–23) |
| day_of_week | int | 0=Monday, 6=Sunday |
| location_id | int | Campus node ID |
| event_flag | int | 1 if event active nearby |
| class_activity | int | 1 if classes in session |
| exam_flag | int | 1 if exam period |
| holiday_flag | int | 1 if holiday |
| historical_crowd | float | Previous crowd level (normalized) |
| crowd_level | str | LOW / MEDIUM / HIGH / VERY_HIGH |

> **Note:** This dataset is synthetic and clearly labeled as such.
> It does not represent real campus measurements.
> A fixed random seed is used for reproducibility.
