# -*- coding: utf-8 -*-
"""
Recompute token-level test metrics (data/test.conll) for all systems and write
report/data/test_metrics_snapshot.json. Run from repo root:

    python report/refresh_test_metrics_snapshot.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pycantonese as pc  # noqa: E402

from report.metric_utils import (  # noqa: E402
    assert_same_length,
    macro_prf_weighted_prf,
    per_label_prf,
    read_gold_tags_test_conll,
    read_pred_tags_mbert_results_conll,
    read_pred_tags_two_column_conll,
)


def _read_sents_for_pc(path: Path):
    sents = []
    cur_t, pairs = None, []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# text = "):
            cur_t = line[len("# text = ") :].strip()
        elif line.startswith("#") or not line.strip():
            if pairs and cur_t is not None:
                sents.append((cur_t, pairs))
            cur_t, pairs = None, []
        elif "\t" in line:
            w, g = line.split("\t", 1)
            pairs.append((w, g.strip()))
    if pairs and cur_t is not None:
        sents.append((cur_t, pairs))
    return sents


def _pc_tag(text: str, tok: str) -> str:
    words = pc.segment(text)
    tagged = pc.pos_tag(words)
    low = {w.lower(): t for w, t in tagged}
    return low.get(tok.lower(), "UNK")


def _pycantonese_preds(test_conll: Path):
    gold, pred = [], []
    for text, pairs in _read_sents_for_pc(test_conll):
        for tok, g in pairs:
            gold.append(g)
            pred.append(_pc_tag(text, tok))
    return gold, pred


def main():
    labels = ["ADJ", "ADV", "INTJ", "NOUN", "PROPN", "VERB", "X"]
    test_conll = ROOT / "data" / "test.conll"

    gold = read_gold_tags_test_conll(test_conll)

    pred_rule = read_pred_tags_two_column_conll(ROOT / "models" / "rule_based" / "results" / "test_pred_recalc.conll")
    pred_bil = read_pred_tags_two_column_conll(
        ROOT / "models" / "bilstm_crf" / "results" / "ensemble_test_pred.conll"
    )
    pred_mb = read_pred_tags_mbert_results_conll(ROOT / "models" / "mbert" / "results" / "test_pred.conll")

    assert_same_length(gold, pred_rule, "rule")
    assert_same_length(gold, pred_bil, "bilstm")
    assert_same_length(gold, pred_mb, "mbert")

    gold_pc, pred_pc = _pycantonese_preds(test_conll)
    assert_same_length(gold, gold_pc, "pyc gold align")
    assert_same_length(gold, pred_pc, "pyc pred align")

    def pack(g, p):
        acc, mp, mr, mf, wp, wr, wf = macro_prf_weighted_prf(g, p)
        return {
            "accuracy": round(acc, 6),
            "macro_precision": round(mp, 6),
            "macro_recall": round(mr, 6),
            "macro_f1": round(mf, 6),
            "weighted_precision": round(wp, 6),
            "weighted_recall": round(wr, 6),
            "weighted_f1": round(wf, 6),
            "num_tokens": len(g),
            "per_label": per_label_prf(g, p, labels),
        }

    snapshot = {
        "test_conll": "data/test.conll",
        "num_tokens": len(gold),
        "labels": labels,
        "PyCantonese": pack(gold_pc, pred_pc),
        "rule_based": pack(gold, pred_rule),
        "bilstm_ensemble": pack(gold, pred_bil),
        "mbert": pack(gold, pred_mb),
    }

    out_dir = ROOT / "report" / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "test_metrics_snapshot.json"
    out_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Wrote", out_path)


if __name__ == "__main__":
    main()
