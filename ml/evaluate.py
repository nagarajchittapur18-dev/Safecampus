"""
SafeCampus AI — Machine Learning Model Evaluation
==================================================
Evaluates the best trained crowd prediction model:
1. Generates classification report (Accuracy, Precision, Recall, F1).
2. Generates and plots the multiclass Confusion Matrix.
3. Computes and plots Feature Importances (where supported by the tree/ensemble model).
4. Saves all figures and CSV tables to `ml/results/`.
"""

import argparse
import sys
from pathlib import Path

# Add project root to sys.path
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from typing import List

import joblib
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for headless plotting
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    classification_report,
    confusion_matrix,
)

from ml.preprocess import FEATURE_COLUMNS


def evaluate_best_model(
    models_dir: str = "ml/models",
    results_dir: str = "ml/results",
) -> None:
    mod_path = Path(models_dir)
    res_path = Path(results_dir)
    res_path.mkdir(parents=True, exist_ok=True)

    model_file = mod_path / "crowd_model.joblib"
    test_split_file = mod_path / "test_split.joblib"
    encoder_file = mod_path / "label_encoder.joblib"

    if not model_file.exists() or not test_split_file.exists():
        raise FileNotFoundError(
            f"Model or test split not found in {models_dir}. Run train.py first."
        )

    print("Loading model and test dataset...")
    model = joblib.load(model_file)
    X_test, y_test = joblib.load(test_split_file)
    le = joblib.load(encoder_file)
    class_names: List[str] = list(le.classes_)

    # Predictions
    y_pred = model.predict(X_test)

    # 1. Classification report
    print("\n" + "=" * 60)
    print("Classification Report:")
    print("=" * 60)
    report_str = classification_report(
        y_test, y_pred, target_names=class_names, digits=4
    )
    print(report_str)

    report_file = res_path / "classification_report.txt"
    report_file.write_text(report_str, encoding="utf-8")
    print(f"Saved classification report to {report_file}")

    # 2. Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    cm_df = pd.DataFrame(cm, index=class_names, columns=class_names)
    cm_csv_path = res_path / "confusion_matrix.csv"
    cm_df.to_csv(cm_csv_path)
    print(f"Saved confusion matrix CSV to {cm_csv_path}")

    fig, ax = plt.subplots(figsize=(7, 6))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_names)
    disp.plot(cmap="Blues", values_format="d", ax=ax, colorbar=True)
    ax.set_title(f"Campus Crowd Prediction — Confusion Matrix\n({type(model).__name__})", fontsize=12, pad=12)
    plt.tight_layout()
    cm_img_path = res_path / "confusion_matrix.png"
    plt.savefig(cm_img_path, dpi=300)
    plt.close()
    print(f"Saved confusion matrix plot to {cm_img_path}")

    # 3. Feature Importance (where supported)
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
        fi_df = pd.DataFrame({
            "feature": FEATURE_COLUMNS,
            "importance": importances,
        }).sort_values(by="importance", ascending=False)

        fi_csv_path = res_path / "feature_importance.csv"
        fi_df.to_csv(fi_csv_path, index=False)
        print(f"Saved feature importance CSV to {fi_csv_path}")

        # Plot
        fig, ax = plt.subplots(figsize=(8, 5))
        y_pos = np.arange(len(fi_df))
        ax.barh(y_pos, fi_df["importance"].iloc[::-1], color="#1565C0", align="center")
        ax.set_yticks(y_pos)
        ax.set_yticklabels(fi_df["feature"].iloc[::-1], fontsize=10)
        ax.set_xlabel("Relative Importance (Gini / Impurity Reduction)", fontsize=11)
        ax.set_title(f"Feature Importance — {type(model).__name__}", fontsize=12, pad=12)
        ax.grid(axis="x", linestyle="--", alpha=0.6)
        plt.tight_layout()
        fi_img_path = res_path / "feature_importance.png"
        plt.savefig(fi_img_path, dpi=300)
        plt.close()
        print(f"Saved feature importance plot to {fi_img_path}")
    else:
        print(f"Model {type(model).__name__} does not expose feature_importances_. Skipped plot.")

    print("\nEvaluation successfully completed!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate best crowd model and generate plots.")
    parser.add_argument("--models", type=str, default="ml/models", help="Models directory")
    parser.add_argument("--results", type=str, default="ml/results", help="Results directory")
    args = parser.parse_args()

    evaluate_best_model(models_dir=args.models, results_dir=args.results)
