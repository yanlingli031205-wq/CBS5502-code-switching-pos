# 本地补跑补充评估（Rule-based 与 BiLSTM）

## 产出图表
- `report\figures\local_per_label_prf_rule_vs_bilstm.png`
- `report\figures\local_confusion_rule_based_test.png`
- `report\figures\local_confusion_bilstm_ensemble_test.png`
- `report\figures\local_generalization_gap_rule_vs_bilstm.png`

## 关键观察
- Rule-based 测试集：Accuracy=1.0000, WeightedF1=1.0000
- BiLSTM ensemble 测试集：Accuracy=0.8061, WeightedF1=0.7913
- BiLSTM 单模型 test vs ensemble：WeightedF1 0.7429 -> 0.7913
- Rule-based 泛化差距（Train/Test WeightedF1）：0.8036 -> 1.0000
- BiLSTM 单模型泛化差距（Train/Test WeightedF1）：0.9910 -> 0.7429

## 重点混淆（Test）
- Rule-based: NOUN->PROPN=0, PROPN->NOUN=0, VERB->NOUN=0, NOUN->VERB=0
- BiLSTM ensemble: NOUN->PROPN=2, PROPN->NOUN=1, VERB->NOUN=2, NOUN->VERB=1
