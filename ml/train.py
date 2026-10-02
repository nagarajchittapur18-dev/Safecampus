"""
SafeCampus AI — Machine Learning Model Training & Comparison
=============================================================
Trains and compares 4 multiclass classification models for campus crowd prediction:
1. Logistic Regression
2. Decision Tree
3. Random Forest
4. Gradient Boosting

Calculates:
- Accuracy
- Precision (macro and weighted)
- Recall (macro and weighted)
- F1-Score (macro and weighted)

Saves comparison to `ml/results/model_comparison.csv` and serializes the best model
to `ml/models/crowd_model.joblib`.
"""

import sys
from pathlib import Path

# Add project root to sys.path
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import argparse
import time
from typing import Any, Dict, Tuple

import joblib
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.tree import DecisionTreeClassifier

from ml.preprocess import (
    FEATURE_COLUMNS,
    load_dataset,
    prepare_features_and_target,
    save_preprocessing_artifacts,
    split_and_scale_data,
)


def train_and_compare_models(
    data_path: str = "ml/data/crowd_data.csv",
    results_dir: str = "ml/results",
    models_dir: str = "ml/models",
    random_state: int = 42,
) -> Tuple[pd.DataFrame, str]:
    """
    Trains all four candidate algorithms and identifies the best performing model.
    """
    print("Loading crowd dataset...")
    df = load_dataset(data_path)
    X, y, le = prepare_features_and_target(df)

    # Use scaled features so Logistic Regression converges properly while trees also benefit
    X_train, X_test, y_train, y_test, scaler = split_and_scale_data(
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

    comparison_records = []
    trained_models = {}

    print(f"\nTraining and evaluating {len(models)} models...")
    print("-" * 75)

    for name, model in models.items():
        t0 = time.perf_counter()
        model.fit(X_train, y_train)
        train_time = time.perf_counter() - t0

        t1 = time.perf_counter()
        y_pred = model.predict(X_test)
        infer_time = (time.perf_counter() - t1) * 1000.0

        acc = accuracy_score(y_test, y_pred)
        prec_w = precision_score(y_test, y_pred, average="weighted", zero_division=0)
        rec_w = recall_score(y_test, y_pred, average="weighted", zero_division=0)
        f1_w = f1_score(y_test, y_pred, average="weighted", zero_division=0)

        prec_m = precision_score(y_test, y_pred, average="macro", zero_division=0)
        rec_m = recall_score(y_test, y_pred, average="macro", zero_division=0)
        f1_m = f1_score(y_test, y_pred, average="macro", zero_division=0)

        record = {
            "model": name,
            "accuracy": round(acc, 4),
            "precision_weighted": round(prec_w, 4),
            "recall_weighted": round(rec_w, 4),
            "f1_weighted": round(f1_w, 4),
            "precision_macro": round(prec_m, 4),
            "recall_macro": round(rec_m, 4),
            "f1_macro": round(f1_m, 4),
            "train_time_sec": round(train_time, 3),
            "inference_time_ms": round(infer_time, 2),
        }
        comparison_records.append(record)
        trained_models[name] = model

        print(
            f"[*] {name:20} | Acc: {acc:.4f} | F1 (weighted): {f1_w:.4f} | "
            f"F1 (macro): {f1_m:.4f} | Train: {train_time:.2f}s"
        )

    res_df = pd.DataFrame(comparison_records).sort_values(by="f1_weighted", ascending=False)

    # Save comparison CSV
    out_dir = Path(results_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    res_path = out_dir / "model_comparison.csv"
    res_df.to_csv(res_path, index=False)
    print("-" * 75)
    print(f"\nModel Comparison Summary:\n{res_df[['model', 'accuracy', 'f1_weighted', 'f1_macro']]}")
    print(f"Saved results to {res_path}")

    # Best model selection
    best_model_name = res_df.iloc[0]["model"]
    best_model = trained_models[best_model_name]
    print(f"\nBest Model Selected: {best_model_name}")

    # Save best model and artifacts
    mod_dir = Path(models_dir)
    mod_dir.mkdir(parents=True, exist_ok=True)
    model_path = mod_dir / "crowd_model.joblib"
    joblib.dump(best_model, model_path)
    print(f"Saved best model to {model_path}")

    save_preprocessing_artifacts(scaler, le, models_dir=models_dir)

    # Also save test data split so evaluate.py can reproduce identical test evaluation
    joblib.dump((X_test, y_test), mod_dir / "test_split.joblib")

    return res_df, best_model_name


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train and compare crowd prediction models.")
    parser.add_argument("--data", type=str, default="ml/data/crowd_data.csv", help="Dataset path")
    parser.add_argument("--results", type=str, default="ml/results", help="Results folder")
    parser.add_argument("--models", type=str, default="ml/models", help="Models folder")
    args = parser.parse_args()

    train_and_compare_models(
        data_path=args.data,
        results_dir=args.results,
        models_dir=args.models,
    )
