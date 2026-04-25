# 基于 README 数据的模型评估与对比

## 数据来源与口径

本评估只使用仓库中已有 README/说明文档的已发布结果，不重新训练模型：

- `models/rule_based/README_rule_based.md`
- `models/bilstm_crf/README_bilstm_crf.md`
- `models/mbert/README_mBERT.md`
- `README.md`（基线与汇总口径）

统一对比维度（可直接横向可比）：

- Test Accuracy
- Test Weighted F1

## 核心结果（测试集）

| 模型 | Accuracy | Weighted F1 |
|---|---:|---:|
| PyCantonese Baseline | 0.4886 | 0.4900 |
| Rule-based | 1.0000 | 1.0000 |
| BiLSTM-CRF（5-seed ensemble） | 0.8061 | 0.7913 |
| mBERT（Advanced Features） | 0.9082 | 0.8530 |

## 相对基线提升（pp）

以 PyCantonese 为基线：

- Rule-based：Accuracy `+51.14`，Weighted F1 `+51.00`
- BiLSTM-CRF：Accuracy `+31.75`，Weighted F1 `+30.13`
- mBERT：Accuracy `+41.96`，Weighted F1 `+36.30`

## 关键分析结论

1. **总体性能排名（测试集）**  
   Rule-based > mBERT > BiLSTM-CRF > PyCantonese。

2. **神经模型对比**  
   mBERT（0.853 F1）优于 BiLSTM-CRF ensemble（0.7913 F1），说明预训练语言知识在小样本混码任务中仍有明显优势。

3. **Rule-based 的解释**  
   Rule-based 在 test 达到 1.0，但在 README 中 train/dev 约 0.80，说明其对当前测试集高度贴合，跨域泛化仍需额外验证。

4. **BiLSTM 的稳定性收益**  
   README 给出单模型 test mean `0.6989 ± 0.0600`（Weighted F1），而 ensemble 提升到 `0.7913`，说明多 seed 集成有效降低波动。

## 可视化图表清单

以下图均已根据 README 数据自动生成至 `report/figures/`：

- `readme_test_overall_accuracy_f1.png`：四模型测试集 Accuracy/F1 总览
- `readme_improvement_vs_baseline.png`：相对基线提升（pp）
- `readme_bilstm_stability_ensemble_gain.png`：BiLSTM 单模型波动 vs ensemble 增益

## 备注

- 本文件为“README 数据复用评估”，不是统一脚本重算结果。
- 对于无法在所有模型统一提供的数据（如全模型 Macro F1、全模型混淆矩阵），已从跨模型主对比图中移除。
