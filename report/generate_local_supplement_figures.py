import json
import os
from collections import Counter

import matplotlib.pyplot as plt
import numpy as np


ROOT = os.path.dirname(os.path.dirname(__file__))
FIG_DIR = os.path.join(ROOT, "report", "figures")


def read_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def read_conll_tags(path):
    y = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            parts = s.split("\t")
            if len(parts) >= 2:
                y.append(parts[1])
    return y


def confusion(y_true, y_pred, labels):
    idx = {l: i for i, l in enumerate(labels)}
    cm = np.zeros((len(labels), len(labels)), dtype=int)
    for g, p in zip(y_true, y_pred):
        if g in idx and p in idx:
            cm[idx[g], idx[p]] += 1
    return cm


def save(fig, filename):
    os.makedirs(FIG_DIR, exist_ok=True)
    path = os.path.join(FIG_DIR, filename)
    fig.tight_layout()
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_per_label_prf(rule_metrics, bilstm_metrics):
    labels = ["ADJ", "ADV", "INTJ", "NOUN", "PROPN", "VERB", "X"]
    metrics = ["precision", "recall", "f1"]
    titles = ["Precision", "Recall", "F1"]

    fig, axes = plt.subplots(1, 3, figsize=(14, 4.6), sharey=True)
    x = np.arange(len(labels))
    w = 0.36

    for i, (m, title) in enumerate(zip(metrics, titles)):
        rvals = [rule_metrics["class_metrics"].get(l, {}).get(m, 0.0) for l in labels]
        bvals = [bilstm_metrics["per_label"].get(l, {}).get(m, 0.0) for l in labels]
        ax = axes[i]
        ax.bar(x - w / 2, rvals, width=w, label="Rule-based")
        ax.bar(x + w / 2, bvals, width=w, label="BiLSTM ensemble")
        ax.set_title(f"Per-label {title} (Test)")
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=25)
        ax.set_ylim(0, 1.05)
        ax.grid(axis="y", linestyle="--", alpha=0.35)
        if i == 0:
            ax.set_ylabel("Score")
            ax.legend()

    return save(fig, "local_per_label_prf_rule_vs_bilstm.png")


def plot_confusion_heatmap(cm, labels, title, filename):
    fig, ax = plt.subplots(figsize=(6.6, 5.8))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_title(title)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Gold")
    ax.set_xticks(np.arange(len(labels)))
    ax.set_yticks(np.arange(len(labels)))
    ax.set_xticklabels(labels, rotation=30)
    ax.set_yticklabels(labels)
    for i in range(len(labels)):
        for j in range(len(labels)):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center", fontsize=8)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    return save(fig, filename)


def plot_generalization_gap(rule_train, rule_dev, rule_test, bil_train, bil_dev, bil_test, bil_ensemble):
    splits = ["Train", "Dev", "Test"]
    rule_acc = [rule_train["accuracy"], rule_dev["accuracy"], rule_test["accuracy"]]
    rule_f1 = [rule_train["weighted_f1"], rule_dev["weighted_f1"], rule_test["weighted_f1"]]
    bil_acc = [bil_train["accuracy"], bil_dev["accuracy"], bil_test["accuracy"]]
    bil_f1 = [bil_train["weighted_f1"], bil_dev["weighted_f1"], bil_test["weighted_f1"]]

    x = np.arange(len(splits))
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), sharex=True)

    axes[0].plot(x, rule_acc, marker="o", linewidth=2, label="Rule-based")
    axes[0].plot(x, bil_acc, marker="s", linewidth=2, label="BiLSTM single-seed")
    axes[0].scatter([2], [bil_ensemble["accuracy"]], marker="*", s=150, label="BiLSTM ensemble test")
    axes[0].set_title("Generalization Gap - Accuracy")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(splits)
    axes[0].set_ylim(0.6, 1.03)
    axes[0].grid(axis="y", linestyle="--", alpha=0.35)
    axes[0].legend()

    axes[1].plot(x, rule_f1, marker="o", linewidth=2, label="Rule-based")
    axes[1].plot(x, bil_f1, marker="s", linewidth=2, label="BiLSTM single-seed")
    axes[1].scatter([2], [bil_ensemble["weighted_f1"]], marker="*", s=150, label="BiLSTM ensemble test")
    axes[1].set_title("Generalization Gap - Weighted F1")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(splits)
    axes[1].set_ylim(0.6, 1.03)
    axes[1].grid(axis="y", linestyle="--", alpha=0.35)
    axes[1].legend()

    return save(fig, "local_generalization_gap_rule_vs_bilstm.png")


def main():
    rule_train = read_json(os.path.join(ROOT, "models", "rule_based", "results", "train_metrics.json"))
    rule_dev = read_json(os.path.join(ROOT, "models", "rule_based", "results", "dev_metrics.json"))
    rule_test = read_json(os.path.join(ROOT, "models", "rule_based", "results", "test_metrics.json"))

    bil_train = read_json(os.path.join(ROOT, "models", "bilstm_crf", "results", "train_metrics.json"))
    bil_dev = read_json(os.path.join(ROOT, "models", "bilstm_crf", "results", "dev_metrics.json"))
    bil_test = read_json(os.path.join(ROOT, "models", "bilstm_crf", "results", "test_metrics.json"))
    bil_ensemble = read_json(os.path.join(ROOT, "models", "bilstm_crf", "results", "ensemble_metrics.json"))

    gold_test = read_conll_tags(os.path.join(ROOT, "data", "test.conll"))
    pred_rule = read_conll_tags(os.path.join(ROOT, "models", "rule_based", "results", "test_pred_recalc.conll"))
    pred_bilstm = read_conll_tags(os.path.join(ROOT, "models", "bilstm_crf", "results", "ensemble_test_pred.conll"))

    labels = ["ADJ", "ADV", "INTJ", "NOUN", "PROPN", "VERB", "X"]
    cm_rule = confusion(gold_test, pred_rule, labels)
    cm_bilstm = confusion(gold_test, pred_bilstm, labels)

    outputs = []
    outputs.append(plot_per_label_prf(rule_test, bil_ensemble))
    outputs.append(plot_confusion_heatmap(cm_rule, labels, "Rule-based Confusion Matrix (Test)", "local_confusion_rule_based_test.png"))
    outputs.append(plot_confusion_heatmap(cm_bilstm, labels, "BiLSTM Ensemble Confusion Matrix (Test)", "local_confusion_bilstm_ensemble_test.png"))
    outputs.append(plot_generalization_gap(rule_train, rule_dev, rule_test, bil_train, bil_dev, bil_test, bil_ensemble))

    n2p_rule = cm_rule[labels.index("NOUN"), labels.index("PROPN")]
    p2n_rule = cm_rule[labels.index("PROPN"), labels.index("NOUN")]
    v2n_rule = cm_rule[labels.index("VERB"), labels.index("NOUN")]
    n2v_rule = cm_rule[labels.index("NOUN"), labels.index("VERB")]
    n2p_bi = cm_bilstm[labels.index("NOUN"), labels.index("PROPN")]
    p2n_bi = cm_bilstm[labels.index("PROPN"), labels.index("NOUN")]
    v2n_bi = cm_bilstm[labels.index("VERB"), labels.index("NOUN")]
    n2v_bi = cm_bilstm[labels.index("NOUN"), labels.index("VERB")]

    summary = os.path.join(ROOT, "report", "local_supplement_evaluation.md")
    with open(summary, "w", encoding="utf-8") as f:
        f.write("# 本地补跑补充评估（Rule-based 与 BiLSTM）\n\n")
        f.write("## 产出图表\n")
        for p in outputs:
            f.write(f"- `{os.path.relpath(p, ROOT)}`\n")
        f.write("\n## 关键观察\n")
        f.write(f"- Rule-based 测试集：Accuracy={rule_test['accuracy']:.4f}, WeightedF1={rule_test['weighted_f1']:.4f}\n")
        f.write(f"- BiLSTM ensemble 测试集：Accuracy={bil_ensemble['accuracy']:.4f}, WeightedF1={bil_ensemble['weighted_f1']:.4f}\n")
        f.write(f"- BiLSTM 单模型 test vs ensemble：WeightedF1 {bil_test['weighted_f1']:.4f} -> {bil_ensemble['weighted_f1']:.4f}\n")
        f.write(f"- Rule-based 泛化差距（Train/Test WeightedF1）：{rule_train['weighted_f1']:.4f} -> {rule_test['weighted_f1']:.4f}\n")
        f.write(f"- BiLSTM 单模型泛化差距（Train/Test WeightedF1）：{bil_train['weighted_f1']:.4f} -> {bil_test['weighted_f1']:.4f}\n")
        f.write("\n## 重点混淆（Test）\n")
        f.write(f"- Rule-based: NOUN->PROPN={n2p_rule}, PROPN->NOUN={p2n_rule}, VERB->NOUN={v2n_rule}, NOUN->VERB={n2v_rule}\n")
        f.write(f"- BiLSTM ensemble: NOUN->PROPN={n2p_bi}, PROPN->NOUN={p2n_bi}, VERB->NOUN={v2n_bi}, NOUN->VERB={n2v_bi}\n")

    print("Generated local supplement figures and summary:")
    for p in outputs:
        print("-", os.path.relpath(p, ROOT))
    print("-", os.path.relpath(summary, ROOT))


if __name__ == "__main__":
    main()
