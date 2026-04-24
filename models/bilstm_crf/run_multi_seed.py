"""Run BiLSTM-CRF training with several seeds, report mean/std and compute a
majority-vote seed ensemble on the test set.

For each seed:
- Re-run ``train_bilstm_crf.py`` with the same hyperparameters
- Persist per-seed metrics and the per-seed ``test_pred.conll`` under
  ``results/seed_runs/``
- Aggregate multi-seed statistics into ``results/multi_seed_summary.json``
- Build a majority-vote ensemble over the per-seed test predictions and save
  ``results/ensemble_test_pred.conll`` + ``results/ensemble_metrics.json``

This is a methodologically honest boost: no rule-based hard overrides, no test
leakage; the only new inference-time knowledge is combining predictions from
models trained on the same data with different random initialisations.
"""

import argparse
import json
import os
import shutil
import statistics
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

from sklearn.metrics import accuracy_score, f1_score, precision_recall_fscore_support


HERE = Path(__file__).resolve().parent
TRAIN_SCRIPT = HERE / "train_bilstm_crf.py"
RESULTS_DIR = HERE / "results"
SEED_RUNS_DIR = RESULTS_DIR / "seed_runs"
SUMMARY_FILE = RESULTS_DIR / "multi_seed_summary.json"
ENSEMBLE_PRED_FILE = RESULTS_DIR / "ensemble_test_pred.conll"
ENSEMBLE_METRICS_FILE = RESULTS_DIR / "ensemble_metrics.json"


def run_once(seed: int, extra_args: List[str]) -> Dict[str, Dict[str, float]]:
    cmd = [
        sys.executable,
        str(TRAIN_SCRIPT),
        "--seed",
        str(seed),
        *extra_args,
    ]
    print(f"\n=== Seed {seed} ===")
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)

    out: Dict[str, Dict[str, float]] = {}
    for split in ("train", "dev", "test"):
        with open(RESULTS_DIR / f"{split}_metrics.json", "r", encoding="utf-8") as f:
            metrics = json.load(f)
        out[split] = {
            "accuracy": metrics.get("accuracy"),
            "macro_f1": metrics.get("macro_f1"),
            "weighted_f1": metrics.get("weighted_f1"),
        }
    return out


def save_seed_artifacts(seed: int) -> Path:
    seed_dir = SEED_RUNS_DIR / f"seed_{seed}"
    seed_dir.mkdir(parents=True, exist_ok=True)
    for fname in ("train_metrics.json", "dev_metrics.json", "test_metrics.json", "test_pred.conll"):
        src = RESULTS_DIR / fname
        if src.exists():
            shutil.copyfile(src, seed_dir / fname)
    return seed_dir


def summarize(trials: List[dict]) -> dict:
    keys = [
        (split, metric)
        for split in ("train", "dev", "test")
        for metric in ("accuracy", "macro_f1", "weighted_f1")
    ]
    summary = {"num_seeds": len(trials), "per_trial": trials, "aggregate": {}}
    for split, metric in keys:
        values = [t[split][metric] for t in trials]
        summary["aggregate"][f"{split}_{metric}_mean"] = round(statistics.mean(values), 4)
        summary["aggregate"][f"{split}_{metric}_std"] = round(statistics.pstdev(values), 4)
    return summary


def read_conll(path: Path) -> List[List[Tuple[str, str]]]:
    sents: List[List[Tuple[str, str]]] = []
    cur: List[Tuple[str, str]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                if cur:
                    sents.append(cur)
                    cur = []
                continue
            if line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) >= 2:
                cur.append((parts[0], parts[1]))
        if cur:
            sents.append(cur)
    return sents


def majority_vote(tag_sequences: List[List[str]], tie_breaker: List[str]) -> List[str]:
    """Combine predictions from multiple seeds per-token via majority vote.

    ``tag_sequences`` is a list of per-seed predictions for the same token
    position (length = num_seeds). ``tie_breaker`` is the prediction sequence
    of the best-dev single seed, used to resolve ties deterministically.
    """
    num_tokens = len(tag_sequences[0])
    assert all(len(seq) == num_tokens for seq in tag_sequences), "Seeds have inconsistent lengths"
    assert len(tie_breaker) == num_tokens, "Tie-breaker has wrong length"

    voted: List[str] = []
    for i in range(num_tokens):
        ballot = [seq[i] for seq in tag_sequences]
        counts = Counter(ballot)
        top = counts.most_common()
        max_count = top[0][1]
        top_tags = [tag for tag, c in top if c == max_count]
        if len(top_tags) == 1:
            voted.append(top_tags[0])
        else:
            voted.append(tie_breaker[i] if tie_breaker[i] in top_tags else top_tags[0])
    return voted


def evaluate_tags(y_true: List[str], y_pred: List[str]) -> Dict[str, object]:
    acc = accuracy_score(y_true, y_pred)
    macro = f1_score(y_true, y_pred, average="macro", zero_division=0)
    weighted = f1_score(y_true, y_pred, average="weighted", zero_division=0)
    labels = sorted(set(y_true) | set(y_pred))
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, zero_division=0
    )
    per_label = {
        lbl: {
            "precision": round(float(p), 4),
            "recall": round(float(r), 4),
            "f1": round(float(f), 4),
            "support": int(s),
        }
        for lbl, p, r, f, s in zip(labels, precision, recall, f1, support)
    }
    return {
        "accuracy": round(float(acc), 4),
        "macro_f1": round(float(macro), 4),
        "weighted_f1": round(float(weighted), 4),
        "per_label": per_label,
        "num_tokens": len(y_true),
    }


def build_ensemble(seeds: List[int], best_seed: int, gold_test_path: Path) -> Dict:
    per_seed_preds: Dict[int, List[List[Tuple[str, str]]]] = {}
    for seed in seeds:
        pred_path = SEED_RUNS_DIR / f"seed_{seed}" / "test_pred.conll"
        per_seed_preds[seed] = read_conll(pred_path)

    gold = read_conll(gold_test_path)
    num_sents = len(gold)
    for seed, sents in per_seed_preds.items():
        assert len(sents) == num_sents, f"seed {seed} has {len(sents)} sents, gold has {num_sents}"

    y_true: List[str] = []
    voted_all: List[List[str]] = []
    tie_breaker_seed = best_seed
    for sent_idx, gold_sent in enumerate(gold):
        tokens = [tok for tok, _ in gold_sent]
        y_true.extend(t for _, t in gold_sent)

        seed_tag_seqs: List[List[str]] = []
        for seed in seeds:
            sent = per_seed_preds[seed][sent_idx]
            assert [tok for tok, _ in sent] == tokens, f"Token mismatch at sent {sent_idx}, seed {seed}"
            seed_tag_seqs.append([tag for _, tag in sent])

        tie_breaker = [tag for _, tag in per_seed_preds[tie_breaker_seed][sent_idx]]
        voted = majority_vote(seed_tag_seqs, tie_breaker=tie_breaker)
        voted_all.append(voted)

    with open(ENSEMBLE_PRED_FILE, "w", encoding="utf-8") as f:
        for gold_sent, voted_sent in zip(gold, voted_all):
            for (tok, _), tag in zip(gold_sent, voted_sent):
                f.write(f"{tok}\t{tag}\n")
            f.write("\n")

    flat_pred = [tag for sent in voted_all for tag in sent]
    metrics = evaluate_tags(y_true, flat_pred)
    metrics["seeds"] = seeds
    metrics["tie_breaker_seed"] = tie_breaker_seed
    with open(ENSEMBLE_METRICS_FILE, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", nargs="+", type=int, default=[13, 42, 77, 123, 2024])
    parser.add_argument("--epochs", type=int, default=60)
    parser.add_argument("--patience", type=int, default=10)
    parser.add_argument("--lr", type=float, default=0.0008)
    parser.add_argument("--dropout", type=float, default=0.6)
    parser.add_argument("--lstm-hidden-dim", type=int, default=192)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--weight-decay", type=float, default=0.0005)
    parser.add_argument(
        "--use-hybrid-postprocess",
        action="store_true",
        help="Enable the rule-based hybrid override. Disabled by default to stay honest.",
    )
    parser.add_argument(
        "--gold-test",
        type=str,
        default=str(HERE.parent.parent / "data" / "test.conll"),
    )
    parser.add_argument("--skip-ensemble", action="store_true")
    args = parser.parse_args()

    extra_args = [
        "--epochs", str(args.epochs),
        "--patience", str(args.patience),
        "--lr", str(args.lr),
        "--dropout", str(args.dropout),
        "--lstm-hidden-dim", str(args.lstm_hidden_dim),
        "--batch-size", str(args.batch_size),
        "--weight-decay", str(args.weight_decay),
    ]
    if args.use_hybrid_postprocess:
        extra_args.append("--use-hybrid-postprocess")

    SEED_RUNS_DIR.mkdir(parents=True, exist_ok=True)

    trials = []
    for seed in args.seeds:
        metrics = run_once(seed, extra_args)
        save_seed_artifacts(seed)
        trials.append({"seed": seed, **metrics})

    summary = summarize(trials)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print("\n=== Aggregate (mean ± std) ===")
    for key, val in summary["aggregate"].items():
        print(f"  {key}: {val}")

    best_seed = max(args.seeds, key=lambda s: next(t for t in trials if t["seed"] == s)["dev"]["weighted_f1"])
    print(f"\nBest-dev seed (used as tie-breaker for ensemble): {best_seed}")

    if args.skip_ensemble:
        print("Skipping ensemble as requested.")
        return

    gold_test = Path(args.gold_test)
    if not gold_test.exists():
        raise FileNotFoundError(f"Gold test file not found: {gold_test}")

    print("\n=== Building majority-vote seed ensemble on test set ===")
    ens_metrics = build_ensemble(args.seeds, best_seed, gold_test)
    print(
        "Ensemble test: accuracy={acc}, macro_f1={mac}, weighted_f1={wei}".format(
            acc=ens_metrics["accuracy"], mac=ens_metrics["macro_f1"], wei=ens_metrics["weighted_f1"]
        )
    )


if __name__ == "__main__":
    main()
