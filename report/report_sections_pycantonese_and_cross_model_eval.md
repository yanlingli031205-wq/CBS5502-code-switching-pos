# Section A: PyCantonese Automatic Annotation (Step 2)

## A1. Background and Objective

In this project, `PyCantonese` was used as the initial automatic POS tagger for English tokens in Cantonese-English code-switched text. The objective at this stage was not to achieve final deployment-level performance, but to provide a fast and structured pre-annotation layer to support downstream manual correction, gold-standard construction, and model development.

## A2. Annotation Pipeline

The Step 2 pipeline was implemented as follows:

1. Extract English tokens from the raw code-switched corpus.
2. Assign initial POS tags using `PyCantonese`.
3. Export structured annotation tables for manual correction of `gold_pos`.
4. Produce cleaned gold data and convert it into a unified CoNLL format for training and evaluation.

## A3. Delivered Outputs

Step 2 generated the required intermediate and final artifacts for subsequent stages:

- Automatically labeled token tables for manual revision;
- Manually corrected `gold_standard_completed.csv`;
- Cleaned training/evaluation file `gold_standard_cleaned.csv`;
- Error analysis materials documenting major annotation failure patterns.

## A4. Baseline Performance and Limitations

Under the project reporting protocol, the PyCantonese baseline achieved:

- **Accuracy:** `48.86%`
- **Weighted F1:** `~0.49`

The primary limitations are:

- Limited disambiguation capacity in code-switched contexts, leading to systematic POS misclassification;
- Weak handling of consecutive English tokens and context-sensitive ambiguities;
- Practical value as a baseline and annotation accelerator, but insufficient quality as a final model.

## A5. Functional Role in the Full Project

Despite its relatively low predictive quality, PyCantonese played a critical methodological role by reducing annotation workload and establishing a consistent baseline for all subsequent methods (`Rule-based`, `BiLSTM-CRF`, and `mBERT`).

---

# Section B: Cross-Model Evaluation

## B1. Evaluation Protocol

To ensure strict comparability across models, this section reports only metrics available for all methods under a shared test setting:

- **Test Accuracy**
- **Test Weighted F1**

Metrics that are not consistently available across all models (e.g., full Macro-F1 coverage, per-label P/R/F1 for every model, and full confusion matrices for every model) are excluded from the main cross-model table and reported only in model-specific supplementary analysis.

## B2. Main Test Results

| Model | Accuracy | Weighted F1 |
|---|---:|---:|
| PyCantonese Baseline | 0.4886 | 0.4900 |
| Rule-based | 1.0000 | 1.0000 |
| BiLSTM-CRF (5-seed Ensemble) | 0.8061 | 0.7913 |
| mBERT (Advanced Features) | 0.9082 | 0.8530 |

## B3. Improvement over Baseline (Percentage Points)

Using PyCantonese as the reference baseline:

- **Rule-based:** Accuracy `+51.14pp`, Weighted F1 `+51.00pp`
- **BiLSTM-CRF:** Accuracy `+31.75pp`, Weighted F1 `+30.13pp`
- **mBERT:** Accuracy `+41.96pp`, Weighted F1 `+36.30pp`

## B4. Comparative Interpretation

1. **Overall ranking on the test set**  
   `Rule-based > mBERT > BiLSTM-CRF > PyCantonese`.

2. **Rule-based vs. neural methods**  
   The rule-based system reaches perfect performance on the current test split, indicating strong rule and lexicon coverage for this data condition. Among neural models, mBERT delivers the best performance, reflecting the benefit of multilingual pretraining in low-resource code-switching settings.

3. **Position of BiLSTM-CRF**  
   BiLSTM-CRF substantially outperforms the baseline and further benefits from multi-seed ensembling. It remains below mBERT but provides a competitive trade-off between complexity, interpretability, and performance.

## B5. Visual Evidence

Primary cross-model figures (comparable metrics only):

- `report/figures/readme_test_overall_accuracy_f1.png`
- `report/figures/readme_improvement_vs_baseline.png`
- `report/figures/readme_bilstm_stability_ensemble_gain.png`

Supplementary model-level analysis figures:

- `report/figures/local_per_label_prf_rule_vs_bilstm.png`
- `report/figures/local_confusion_rule_based_test.png`
- `report/figures/local_confusion_bilstm_ensemble_test.png`
- `report/figures/local_generalization_gap_rule_vs_bilstm.png`

## B6. Section Conclusion

All three improved methods significantly surpass the PyCantonese baseline. The rule-based system delivers the strongest result on the current test set, mBERT is the strongest neural approach, and BiLSTM-CRF achieves consistent gains through feature injection and ensembling. Overall, the empirical evidence supports both the project’s modeling choices and its staged improvement strategy.
