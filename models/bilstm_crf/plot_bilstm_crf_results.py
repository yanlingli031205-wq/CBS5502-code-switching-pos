import json
import os
from typing import Dict, Tuple

import matplotlib.pyplot as plt
import numpy as np


def read_metric(path: str) -> Tuple[float, float]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return float(data["weighted_f1"]), float(data["accuracy"])


def safe_read_metric(path: str, fallback: Tuple[float, float]) -> Tuple[float, float]:
    if os.path.exists(path):
        return read_metric(path)
    return fallback


def main() -> None:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
    results_dir = os.path.join(current_dir, "results")
    os.makedirs(results_dir, exist_ok=True)

    ensemble_path = os.path.join(results_dir, "ensemble_metrics.json")
    bilstm_metric = (
        read_metric(ensemble_path)
        if os.path.exists(ensemble_path)
        else read_metric(os.path.join(results_dir, "test_metrics.json"))
    )
    bilstm_label = (
        "BiLSTM-CRF + Features\n5-seed Ensemble (zxy)"
        if os.path.exists(ensemble_path)
        else "BiLSTM-CRF + Features\n(zxy, best seed)"
    )

    model_metrics: Dict[str, Tuple[float, float]] = {
        "PyCantonese (Baseline)": (0.49, 0.4886),
        "mBERT + Advanced Feat.": (0.853, 0.9082),
        "Rule-based (lyl)": safe_read_metric(
            os.path.join(root_dir, "models", "rule_based", "results", "test_metrics.json"),
            (1.0, 1.0),
        ),
        bilstm_label: bilstm_metric,
    }

    models = list(model_metrics.keys())
    f1_scores = [model_metrics[m][0] for m in models]
    accuracy_scores = [model_metrics[m][1] for m in models]

    x = np.arange(len(models))
    width = 0.35

    fig, ax = plt.subplots(figsize=(11, 7))
    rects1 = ax.bar(x - width / 2, f1_scores, width, label="Weighted F1", color="#5DADE2")
    rects2 = ax.bar(x + width / 2, accuracy_scores, width, label="Accuracy", color="#F1948A")

    ax.set_ylabel("Score")
    ax.set_title("POS Tagging Model Comparison (Test Set)")
    ax.set_xticks(x)
    ax.set_xticklabels(models, rotation=15, ha="right")
    ax.set_ylim(0, 1.1)
    ax.legend()

    for rect in list(rects1) + list(rects2):
        h = rect.get_height()
        ax.annotate(
            f"{h:.3f}",
            xy=(rect.get_x() + rect.get_width() / 2, h),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    fig.tight_layout()
    output_path = os.path.join(results_dir, "bilstm_crf_model_comparison.png")
    plt.savefig(output_path, dpi=300)
    print(f"Saved figure to: {output_path}")


if __name__ == "__main__":
    main()
