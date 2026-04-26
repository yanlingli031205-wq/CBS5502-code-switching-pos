# -*- coding: utf-8 -*-
"""Shared helpers: read gold/pred CoNLL-style tags and compute test-set metrics."""
from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)


def read_gold_tags_test_conll(path: Path) -> List[str]:
    tags: List[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("#") or not line.strip():
            continue
        if "\t" in line:
            tags.append(line.split("\t", 1)[1].strip())
    return tags


def read_pred_tags_two_column_conll(path: Path) -> List[str]:
    """Second column is the predicted POS (Rule-based / BiLSTM exports)."""
    tags: List[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("#") or not line.strip():
            continue
        if "\t" in line:
            tags.append(line.split("\t", 1)[1].strip())
    return tags


def read_pred_tags_mbert_results_conll(path: Path) -> List[str]:
    """models/mbert/results/test_pred.conll: lines like `token [FEAT_X] ... POS`."""
    tags: List[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        parts = s.split()
        tags.append(parts[-1].strip())
    return tags


def assert_same_length(gold: List[str], pred: List[str], name: str) -> None:
    if len(gold) != len(pred):
        raise ValueError(f"{name}: gold len {len(gold)} != pred len {len(pred)}")


def macro_prf_weighted_prf(gold: List[str], pred: List[str]) -> Tuple[float, float, float, float, float, float, float]:
    acc = float(accuracy_score(gold, pred))
    mp = float(precision_score(gold, pred, average="macro", zero_division=0))
    mr = float(recall_score(gold, pred, average="macro", zero_division=0))
    mf = float(f1_score(gold, pred, average="macro", zero_division=0))
    wp = float(precision_score(gold, pred, average="weighted", zero_division=0))
    wr = float(recall_score(gold, pred, average="weighted", zero_division=0))
    wf = float(f1_score(gold, pred, average="weighted", zero_division=0))
    return acc, mp, mr, mf, wp, wr, wf


def per_label_prf(gold: List[str], pred: List[str], labels: List[str]) -> dict:
    out: dict = {}
    for lab in labels:
        tp = sum(1 for g, p in zip(gold, pred) if g == lab and p == lab)
        fp = sum(1 for g, p in zip(gold, pred) if g != lab and p == lab)
        fn = sum(1 for g, p in zip(gold, pred) if g == lab and p != lab)
        p_d = tp + fp
        r_d = tp + fn
        prec = tp / p_d if p_d else 0.0
        rec = tp / r_d if r_d else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
        sup = sum(1 for g in gold if g == lab)
        out[lab] = {
            "precision": round(prec, 6),
            "recall": round(rec, 6),
            "f1": round(f1, 6),
            "support": sup,
        }
    return out


def confusion_counts(gold: List[str], pred: List[str], labels: List[str]):
    return confusion_matrix(gold, pred, labels=labels)
