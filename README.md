# CBS5502 Group Project — Code-Switching POS Tagging

## Project Overview

This project studies Cantonese-English code-switching POS tagging. We compare four approaches under a shared data protocol:

- PyCantonese baseline
- Rule-based system
- BiLSTM-CRF
- mBERT fine-tuning

---

## Team Roles

| Member | Responsibility | Status |
|------|------|------|
| zqy | Step 1 Data collection | Completed |
| pyt | Step 2 PyCantonese auto annotation | Completed |
| lyl | Step 3 Gold Standard annotation + Step 4a Rule-based | Completed (2026-04-22) |
| zxy | Step 4b BiLSTM-CRF | Completed (2026-04-24) |
| szq | Step 4c mBERT fine-tuning | Completed (2026-04-23) |
| pyt | Step 5 Evaluation and cross-model comparison | Pending |

---

## Repository Structure

```text
CBS5502-code-switching-pos/
├── corpus/                              # Raw corpus files
│   ├── CBS5502group.xlsx
│   ├── token_langid_all.csv
│   └── english_tokens.csv
│
├── annotation/
│   ├── gold_standard/
│   └── error_analysis/
│
├── data/                                # Shared Step 4 CoNLL split
│   ├── train.conll                      # 216 sentences, 388 tokens
│   ├── dev.conll                        # 46 sentences, 76 tokens
│   └── test.conll                       # 47 sentences, 98 tokens
│
├── models/
│   ├── Step 4 shared guidance note         # Shared guidance and targets
│   ├── rule_based/                      # Step 4a (lyl)
│   │   ├── rule_based_tagger.py
│   │   ├── README_rule_based.md
│   │   └── results/
│   ├── bilstm_crf/                      # Step 4b (zxy)
│   │   ├── train_bilstm_crf.py
│   │   ├── run_multi_seed.py
│   │   ├── plot_bilstm_crf_results.py
│   │   ├── README_bilstm_crf.md
│   │   └── results/
│   └── mbert/                           # Step 4c (szq)
│       └── README_mBERT.md
│
├── evaluation/
├── scripts/
├── report/
├── reference/
└── README.md
```

---

## Shared Data Protocol (Step 4)

All model owners use the same CoNLL split:

- `data/train.conll` for training
- `data/dev.conll` for validation and hyperparameter tuning
- `data/test.conll` for final evaluation only

Format:

- Two columns: `token<TAB>gold_pos`
- Blank line separates sentences
- Optional comment lines: `# sent_id`, `# text`

---

## Step 3 (lyl) — Gold Standard and Error Analysis

### Gold Standard annotation

- 335 annotated sentences in total
- 310 cleaned sentences after removing rows containing unrecognized `/` tokens
- 569 English tokens in the cleaned file
- PyCantonese baseline accuracy on cleaned set: **48.86%**

### Error analysis

71 annotation error cases were categorized. The major recurring issue is over-tagging as `PROPN`, plus frequent ambiguity between `NOUN/VERB/ADJ`.

---

## Step 4a (lyl) — Rule-based POS Tagger

Delivered:

- `models/rule_based/rule_based_tagger.py`
- 7 lexicons + prioritized rule chain + Cantonese-context disambiguation rules

Results:

- Test set: Accuracy **100%**, Weighted F1 **1.0000**
- Train set: Accuracy **80.93%**, Weighted F1 **0.8036**

---

## Step 4b (zxy) — BiLSTM-CRF

Delivered:

- `train_bilstm_crf.py`: BiLSTM-CRF training with feature injection
- `run_multi_seed.py`: 5-seed training and majority-vote ensemble
- `plot_bilstm_crf_results.py`: comparison figure generation
- `README_bilstm_crf.md`: full technical record

Method highlights:

- BiLSTM-CRF backbone with char encoder + CRF decoding
- 15-dim injected features from rule-based resources
- regularization tuning (`dropout`, `weight_decay`)
- 5-seed majority-vote ensemble for stability

Final results:

- Best single-seed test weighted F1: **0.7429**
- 5-seed ensemble test weighted F1: **0.7913**
- 5-seed ensemble test accuracy: **0.8061**

---

## Step 4c (szq) — mBERT Fine-tuning

Delivered:

- `models/mbert/train_with_advanced_features.py`
- `README_mBERT.md`

Method:

- Fine-tuning `bert-base-multilingual-cased`
- Lexicon and contextual feature injection

Final result:

- Test F1: **0.853**
- Test Accuracy: **90.82%**

---

## GitHub Repository

Repository URL:

- [https://github.com/yanlingli031205-wq/CBS5502-code-switching-pos](https://github.com/yanlingli031205-wq/CBS5502-code-switching-pos)

Clone:

```bash
git clone https://github.com/yanlingli031205-wq/CBS5502-code-switching-pos.git
```

Commit and push:

```bash
git add .
git commit -m "Describe your update"
git push
```

