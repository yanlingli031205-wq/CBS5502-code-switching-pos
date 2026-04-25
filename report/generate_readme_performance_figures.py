import os
import numpy as np
import matplotlib.pyplot as plt


FIG_DIR = os.path.join("report", "figures")


def ensure_dir():
    os.makedirs(FIG_DIR, exist_ok=True)


def save(fig, name):
    path = os.path.join(FIG_DIR, name)
    fig.tight_layout()
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_test_overall():
    models = ["PyCantonese", "Rule-based", "BiLSTM-CRF", "mBERT"]
    accuracy = [0.4886, 1.0000, 0.8061, 0.9082]
    weighted_f1 = [0.4900, 1.0000, 0.7913, 0.8530]

    x = np.arange(len(models))
    w = 0.36
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    ax.bar(x - w / 2, accuracy, width=w, label="Accuracy")
    ax.bar(x + w / 2, weighted_f1, width=w, label="Weighted F1")
    ax.set_title("Test Set Performance from README Data")
    ax.set_ylabel("Score")
    ax.set_ylim(0, 1.05)
    ax.set_xticks(x)
    ax.set_xticklabels(models, rotation=10)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    ax.legend()

    for i, v in enumerate(accuracy):
        ax.text(i - w / 2, v + 0.015, f"{v:.3f}", ha="center", fontsize=8)
    for i, v in enumerate(weighted_f1):
        ax.text(i + w / 2, v + 0.015, f"{v:.3f}", ha="center", fontsize=8)
    return save(fig, "readme_test_overall_accuracy_f1.png")


def plot_improvement_vs_baseline():
    models = ["Rule-based", "BiLSTM-CRF", "mBERT"]
    baseline_acc = 0.4886
    baseline_f1 = 0.4900
    acc = [1.0000, 0.8061, 0.9082]
    f1 = [1.0000, 0.7913, 0.8530]

    acc_pp = [(v - baseline_acc) * 100 for v in acc]
    f1_pp = [(v - baseline_f1) * 100 for v in f1]

    x = np.arange(len(models))
    w = 0.36
    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    ax.bar(x - w / 2, acc_pp, width=w, label="Accuracy gain (pp)")
    ax.bar(x + w / 2, f1_pp, width=w, label="Weighted F1 gain (pp)")
    ax.set_title("Improvement over PyCantonese Baseline")
    ax.set_ylabel("Percentage points (pp)")
    ax.set_xticks(x)
    ax.set_xticklabels(models)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    ax.legend()

    for i, v in enumerate(acc_pp):
        ax.text(i - w / 2, v + 0.7, f"+{v:.1f}", ha="center", fontsize=8)
    for i, v in enumerate(f1_pp):
        ax.text(i + w / 2, v + 0.7, f"+{v:.1f}", ha="center", fontsize=8)
    return save(fig, "readme_improvement_vs_baseline.png")


def plot_bilstm_stability():
    labels = ["Single mean", "Single +1 std", "Single -1 std", "Ensemble"]
    acc_vals = [0.7061, 0.7061 + 0.0634, 0.7061 - 0.0634, 0.8061]
    f1_vals = [0.6989, 0.6989 + 0.0600, 0.6989 - 0.0600, 0.7913]

    x = np.arange(len(labels))
    w = 0.36
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    ax.bar(x - w / 2, acc_vals, width=w, label="Accuracy")
    ax.bar(x + w / 2, f1_vals, width=w, label="Weighted F1")
    ax.set_title("BiLSTM-CRF Stability and Ensemble Gain")
    ax.set_ylabel("Score")
    ax.set_ylim(0.55, 0.90)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=10)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    ax.legend()
    return save(fig, "readme_bilstm_stability_ensemble_gain.png")


def main():
    ensure_dir()
    outputs = [
        plot_test_overall(),
        plot_improvement_vs_baseline(),
        plot_bilstm_stability(),
    ]
    print("Generated figures:")
    for p in outputs:
        print("-", p)


if __name__ == "__main__":
    main()
