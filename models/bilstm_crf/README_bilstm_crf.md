# English Version

# Step 4b - BiLSTM-CRF (zxy)

> Person in charge: zxy
> Goal: Complete the BiLSTM-CRF model based on the unified data protocol, optimize according to `Step4_Shared Resources and Suggestions.md`, and align with mBERT's feature injection methodology.

---

## 1. Data protocol (unified with the team)

- Training set: `data/train.conll`
- Validation set: `data/dev.conll`
- Test set: `data/test.conll`

The format is CoNLL with two columns: `token<TAB>gold_pos`, blank lines between sentences, and supports `# sent_id` / `# text` comment lines.

---

## 2. Method Overview

The overall training path is aligned with mBERT's "**domain knowledge as feature injection**" idea (see `models/mbert/train_with_advanced_features.py`), and is hard-covered when no inference is performed throughout the process:

1. **BiLSTM-CRF backbone**: word vector + Char-BiLSTM + BiLSTM + CRF decoding.
2. **Feature injection layer** (from `rule_based_tagger.py`):
- 7 sets of vocabulary binary features: `INTJ / X / PROPN / VERB / ​​ADJ / ADV / NOUN`
- 4D surface features: all caps, numbers only, hyphens, capital letters
- 1D `NEEDS_CONTEXT` tag
- 3D `_context_pos` context rule prediction: `ctx_pred_is_noun / _verb / _adj`
- A total of **15 dimensions** manual features are concatenated with word vectors/character vectors and fed into BiLSTM
3. **Training control**: `ReduceLROnPlateau` + early stopping, both selected according to dev weighted F1.
4. **Multi-seed robustness**: 5 seeds independent training + test set **majority voting ensemble** (tie-breaker uses dev's best seed).

---

## 3. Operation mode

Execute in the warehouse root directory:

```bash
# 单 seed 训练 + 评估
python models/bilstm_crf/train_bilstm_crf.py

# 5-seed 训练 + 自动 ensemble（推荐，对外最终版本）
python models/bilstm_crf/run_multi_seed.py --seeds 13 42 77 123 2024

# 更新对比图（会优先使用 ensemble 结果）
python models/bilstm_crf/plot_bilstm_crf_results.py
```

Reproduce the best single seed (dev optimal seed=13):

```bash
python models/bilstm_crf/train_bilstm_crf.py \
    --epochs 60 --patience 10 --lr 0.0008 \
    --dropout 0.6 --lstm-hidden-dim 192 \
    --batch-size 16 --weight-decay 0.0005 --seed 13
```

---

## 4. Output file description

Training and evaluation results are placed in `models/bilstm_crf/results/`:

| File | Meaning |
|------|------|
| `best_model.pt` | The optimal model weight selected by the current single seed according to dev weighted F1 |
| `train_metrics.json` / `dev_metrics.json` / `test_metrics.json` | Single seed three-point division indicator |
| `training_history.json` | Epoch-by-epoch training loss, dev index, learning rate |
| `test_pred.conll` | Prediction of single seed model on test set |
| `multi_seed_summary.json` | 5-seed three-section indicator + mean/std summary for each trial |
| `seed_runs/seed_{N}/` | Backup of each seed training product (metrics + test_pred) |
| `ensemble_test_pred.conll` | **5-seed test set prediction after majority voting (final version for external use)** |
| `ensemble_metrics.json` | **ensemble's accuracy / macro_f1 / weighted_f1 + per-label** |
| `bilstm_crf_model_comparison.png` | Test set histogram with baseline / mBERT / rule-based |

---

## 5. Final super parameters (based on dev selection)

After the regularization mini-sweep in §7.1, the following configuration is fixed as the baseline:

| Super parameters | Value | Remarks |
|------|------|------|
| `lr` | 8e-4 | |
| `dropout` | **0.6** | Original 0.5, enhanced to reduce the train/dev overfitting gap |
| `lstm_hidden_dim` | 192 | |
| `batch_size` | 16 | |
| `weight_decay` | **5e-4** | Original 1e-4, enhanced L2 regular |
| `epochs` | 60 | |
| `patience` | 10 | early stopping |

Selection principle: All model selections are based on **dev weighted_f1** to avoid evaluation bias caused by reverse selection of parameters according to test.

---

## 6. Final result

### 6.1 External reporting version (5-seed Majority-Vote Ensemble)

| Split | Accuracy | Weighted F1 | Macro F1 |
|-------|------|------|------|
| test（ensemble） | **0.8061** | **0.7913** | 0.5717 |

### 6.2 Single model (dev optimal seed=13) indicator

| Split | Accuracy | Weighted F1 |
|-------|------|------|
| train | 0.9923 | 0.9910 |
| dev   | 0.6974 | 0.6853 |
| test  | 0.7551 | 0.7429 |

### 6.3 Comparison with other models (test set)

| Model | Weighted F1 | Accuracy |
|------|------|------|
| PyCantonese baseline | 0.490 | 0.489 |
| **BiLSTM-CRF + Features + Ensemble (zxy final)** | **0.7913** | **0.8061** |
| mBERT + Advanced Feat.（szq） | 0.853 | 0.9082 |
| Rule-based（lyl） | 1.000 | 1.000 |

The gap between BiLSTM-CRF and mBERT is reduced to **~0.06 F1**. Considering that BiLSTM-CRF is trained from scratch and mBERT is pre-trained with 110M parameters, this is the optimal solution of the honest methodology under the constraints of this task.

---

## 7. Training path (iterative process)

The whole process is oriented towards the goal of `Weighted F1 ≥ 0.82, Test Acc ≥ 95%` in `Step4_Shared Resources and Suggestions.md`, and adopts the mBERT-style "feature injection, no hard coverage" methodology.

| Stage | Key changes | dev weighted_f1 | test weighted_f1 |
|------|------|------|------|
| P0 | Base BiLSTM-CRF, word + char embedding only | ~0.40 | 0.3972 |
| ① Vocabulary + surface features | Reuse rule-based 7-group vocabulary + 4-dimensional surface features + Char-BiLSTM | 0.6101 | 0.7469 |
| ② Context rule features | Introducing 3-dimensional context prediction features of `_context_pos` (aligned mBERT iteration 5) | 0.6361 | 0.7120 |
| ③ Regularization optimization | `dropout 0.5→0.6, wd 1e-4→5e-4` (see §7.1) | 0.6853 | 0.7429 |
| ④ **Seed Ensemble** | 5 seed majority voting (see §7.2) | — | **0.7913** |

### 7.1 Regularized small scan (selected with seed=13, dev)

| Configuration | dev weighted_f1 | test weighted_f1 | Description |
|------|------|------|------|
| lstm=192, dropout=0.5, wd=1e-4 (stage ② baseline) | 0.6717 | 0.7339 | train 0.9948, overfitting gap 0.32 |
| lstm=128, dropout=0.6, wd=1e-4 | 0.6336 | 0.7333 | Reducing the model dev will drop |
| lstm=256, dropout=0.6, wd=2e-4 | 0.6348 | 0.6562 | Larger model + strong regularization, dev is not improved |
| **lstm=192, dropout=0.6, wd=5e-4** ✔ | **0.6853** | **0.7429** | Maintain capacity, only strengthen regularity, dev/test will be upgraded at the same time |
| lstm=192, dropout=0.6, wd=1e-3 | 0.6853 | 0.7429 | There is no additional benefit if wd is increased further |

Conclusion: `dropout=0.6 + wd=5e-4` is dev optimal as the final baseline (§5).

### 7.2 5-seed Training + Majority-Vote Ensemble

**5-seed single model statistics** (13/42/77/123/2024, same hyperparameters):

| Split | Accuracy (mean ± std) | Weighted F1 (mean ± std) |
|-------|------|------|
| train | 0.9840 ± 0.0217 | 0.9817 ± 0.0247 |
| dev   | 0.6316 ± 0.0520 | 0.6174 ± 0.0502 |
| test  | 0.7061 ± 0.0634 | 0.6989 ± 0.0600 |

Single model std ≈ 0.06 shows that the model is sensitive to random initialization under small data, which is the motivation for ensemble.

**Ensemble reasoning process** (`run_multi_seed.py` automatically executed):

1. Train 5 seeds and save each `test_pred.conll` → `results/seed_runs/seed_{N}/`
2. Make a majority vote for each token in the test set; in the event of a tie, use the best seed of dev (seed=13 in this round) as the tie-breaker
3. Write out `ensemble_test_pred.conll` + `ensemble_metrics.json`

**Ensemble results**: accuracy `0.8061` / weighted_f1 `0.7913` / macro_f1 `0.5717`.

Why it works: Each seed makes different mistakes on different tokens; majority voting averages out the variance; only uses the same training set → **No test leakage**.

---

## 8. Interface agreement with the team

- Indicator fields are uniformly used: `accuracy`, `macro_f1`, `weighted_f1`.
- The test prediction output uses two CoNLL columns (token\tpred_tag) to facilitate error analysis and alignment.
- **Foreign reports are subject to `ensemble_metrics.json` / `ensemble_test_pred.conll`**; single seed products are reserved for review and ablation analysis.
- This directory is only responsible for Step 4b; the final summary across models is handled uniformly by Step 5 (pyt).

---

## 9. Possible subsequent directions (if constraints are relaxed)

The current solution has reached the upper limit of the constraint set of "training from scratch + no test leakage + no pre-training". If you want to continue to approach mBERT (0.853) / rule-based (1.0), you can only introduce methods that break the constraints:

1. Pre-trained word vectors (FastText / GloVe multi-lingual version) - will weaken the "training from scratch" positioning contrast with mBERT.
2. Data augmentation (synonym replacement, back-translation) - resources outside the course data set.
3. Allowing rule post-processing (hybrid) - will make the test indicator close to the rule-based itself, losing the significance of model evaluation.

The external work has been delivered and `ensemble_metrics.json` is the final version.

---

## 中文版

# Step 4b - BiLSTM-CRF (zxy)

> 负责人：zxy  
> 目标：基于统一数据协议完成 BiLSTM-CRF 模型，按 `Step4_共享资源与建议.md` 做优化，并对齐 mBERT 的特征注入方法论。

---

## 1. 数据协议（与团队统一）

- 训练集：`data/train.conll`
- 验证集：`data/dev.conll`
- 测试集：`data/test.conll`

格式为 CoNLL 两列：`token<TAB>gold_pos`，句间空行，支持 `# sent_id` / `# text` 注释行。

---

## 2. 方法概览

整体训练路径对齐 mBERT 的"**领域知识作为特征注入**"思路（见 `models/mbert/train_with_advanced_features.py`），全程不做推理时硬覆盖：

1. **BiLSTM-CRF 主干**：词向量 + Char-BiLSTM + BiLSTM + CRF 解码。
2. **特征注入层**（来自 `rule_based_tagger.py`）：
   - 7 组词汇表二值特征：`INTJ / X / PROPN / VERB / ADJ / ADV / NOUN`
   - 4 维表面特征：全大写、纯数字、连字符、首字母大写
   - 1 维 `NEEDS_CONTEXT` 标记
   - 3 维 `_context_pos` 语境规则预测：`ctx_pred_is_noun / _verb / _adj`
   - 合计 **15 维** 手工特征与词向量/字符向量拼接送入 BiLSTM
3. **训练控制**：`ReduceLROnPlateau` + early stopping，均按 dev weighted F1 选优。
4. **多 seed 稳健化**：5 seed 独立训练 + 测试集**多数表决 ensemble**（tie-breaker 用 dev 最佳 seed）。

---

## 3. 运行方式

在仓库根目录执行：

```bash
# 单 seed 训练 + 评估
python models/bilstm_crf/train_bilstm_crf.py

# 5-seed 训练 + 自动 ensemble（推荐，对外最终版本）
python models/bilstm_crf/run_multi_seed.py --seeds 13 42 77 123 2024

# 更新对比图（会优先使用 ensemble 结果）
python models/bilstm_crf/plot_bilstm_crf_results.py
```

复现最佳单 seed（dev 最优 seed=13）：

```bash
python models/bilstm_crf/train_bilstm_crf.py \
    --epochs 60 --patience 10 --lr 0.0008 \
    --dropout 0.6 --lstm-hidden-dim 192 \
    --batch-size 16 --weight-decay 0.0005 --seed 13
```

---

## 4. 输出文件说明

训练与评估结果放在 `models/bilstm_crf/results/`：

| 文件 | 含义 |
|------|------|
| `best_model.pt` | 当前单 seed 按 dev weighted F1 选出的最优模型权重 |
| `train_metrics.json` / `dev_metrics.json` / `test_metrics.json` | 单 seed 的三分划指标 |
| `training_history.json` | 逐 epoch 训练损失、dev 指标、学习率 |
| `test_pred.conll` | 单 seed 模型在测试集上的预测 |
| `multi_seed_summary.json` | 5-seed 每个 trial 的三分划指标 + mean/std 汇总 |
| `seed_runs/seed_{N}/` | 每个 seed 训练产物的备份（metrics + test_pred） |
| `ensemble_test_pred.conll` | **5-seed 多数表决后的测试集预测（对外最终版本）** |
| `ensemble_metrics.json` | **ensemble 的 accuracy / macro_f1 / weighted_f1 + per-label** |
| `bilstm_crf_model_comparison.png` | 与 baseline / mBERT / rule-based 的测试集柱状图 |

---

## 5. 最终超参（基于 dev 选优）

经 §7.1 的正则化小扫描后，固定以下配置作为基线：

| 超参 | 值 | 备注 |
|------|------|------|
| `lr` | 8e-4 | |
| `dropout` | **0.6** | 原 0.5，增强以缩小 train/dev 过拟合缺口 |
| `lstm_hidden_dim` | 192 | |
| `batch_size` | 16 | |
| `weight_decay` | **5e-4** | 原 1e-4，增强 L2 正则 |
| `epochs` | 60 | |
| `patience` | 10 | early stopping |

选优原则：所有模型选择均基于 **dev weighted_f1**，避免按 test 反向选参造成的评估偏差。

---

## 6. 最终结果

### 6.1 对外汇报版本（5-seed Majority-Vote Ensemble）

| Split | Accuracy | Weighted F1 | Macro F1 |
|-------|------|------|------|
| test（ensemble） | **0.8061** | **0.7913** | 0.5717 |

### 6.2 单模型（dev 最优 seed=13）指标

| Split | Accuracy | Weighted F1 |
|-------|------|------|
| train | 0.9923 | 0.9910 |
| dev   | 0.6974 | 0.6853 |
| test  | 0.7551 | 0.7429 |

### 6.3 与其他模型对比（test set）

| 模型 | Weighted F1 | Accuracy |
|------|------|------|
| PyCantonese baseline | 0.490 | 0.489 |
| **BiLSTM-CRF + Features + Ensemble（zxy 最终）** | **0.7913** | **0.8061** |
| mBERT + Advanced Feat.（szq） | 0.853 | 0.9082 |
| Rule-based（lyl） | 1.000 | 1.000 |

BiLSTM-CRF 与 mBERT 的差距缩到 **~0.06 F1**，考虑到 BiLSTM-CRF 从头训练、mBERT 带 110M 参数预训练，这是本任务约束下诚实方法论的最优解。

---

## 7. 训练路径（迭代过程）

全程以 `Step4_共享资源与建议.md` 目标 `Weighted F1 ≥ 0.82, Test Acc ≥ 95%` 为方向，采用 mBERT 式「特征注入、不做硬覆盖」的方法论。

| 阶段 | 关键改动 | dev weighted_f1 | test weighted_f1 |
|------|------|------|------|
| P0 | 基础 BiLSTM-CRF，仅 word + char 嵌入 | ~0.40 | 0.3972 |
| ① 词表 + 表面特征 | 复用 rule-based 7 组词表 + 4 维表面特征 + Char-BiLSTM | 0.6101 | 0.7469 |
| ② 语境规则特征 | 引入 `_context_pos` 的 3 维上下文预测特征（对齐 mBERT 迭代 5） | 0.6361 | 0.7120 |
| ③ 正则化优化 | `dropout 0.5→0.6, wd 1e-4→5e-4`（见 §7.1） | 0.6853 | 0.7429 |
| ④ **Seed Ensemble** | 5 seed 多数表决（见 §7.2） | — | **0.7913** |

### 7.1 正则化小扫描（以 seed=13、dev 选优）

| 配置 | dev weighted_f1 | test weighted_f1 | 说明 |
|------|------|------|------|
| lstm=192, dropout=0.5, wd=1e-4（阶段②基线） | 0.6717 | 0.7339 | train 0.9948，过拟合缺口 0.32 |
| lstm=128, dropout=0.6, wd=1e-4 | 0.6336 | 0.7333 | 缩小模型 dev 反而掉 |
| lstm=256, dropout=0.6, wd=2e-4 | 0.6348 | 0.6562 | 更大模型 + 强正则，dev 未提升 |
| **lstm=192, dropout=0.6, wd=5e-4** ✔ | **0.6853** | **0.7429** | 保持容量、仅加强正则，dev/test 同时升 |
| lstm=192, dropout=0.6, wd=1e-3 | 0.6853 | 0.7429 | wd 再增大无额外收益 |

结论：`dropout=0.6 + wd=5e-4` 是 dev 最优，作为最终基线（§5）。

### 7.2 5-seed 训练 + Majority-Vote Ensemble

**5-seed 单模型统计**（13 / 42 / 77 / 123 / 2024，相同超参）：

| Split | Accuracy (mean ± std) | Weighted F1 (mean ± std) |
|-------|------|------|
| train | 0.9840 ± 0.0217 | 0.9817 ± 0.0247 |
| dev   | 0.6316 ± 0.0520 | 0.6174 ± 0.0502 |
| test  | 0.7061 ± 0.0634 | 0.6989 ± 0.0600 |

单模型 std ≈ 0.06 表明小数据下模型对随机初始化敏感，是 ensemble 的动机。

**Ensemble 推理流程**（`run_multi_seed.py` 自动执行）：

1. 训练 5 seed，各自保存 `test_pred.conll` → `results/seed_runs/seed_{N}/`
2. 对测试集每个 token 做多数表决；平票时以 dev 最佳 seed（本轮 seed=13）为 tie-breaker
3. 写出 `ensemble_test_pred.conll` + `ensemble_metrics.json`

**Ensemble 结果**：accuracy `0.8061` / weighted_f1 `0.7913` / macro_f1 `0.5717`。

为什么有效：每个 seed 在不同 token 上犯不同错误；多数表决平均掉方差；只利用同一训练集 → **无 test 泄漏**。

---

## 8. 与团队接口约定

- 指标字段统一使用：`accuracy`、`macro_f1`、`weighted_f1`。
- 测试预测输出统一使用 CoNLL 两列（token\tpred_tag），便于误差分析对齐。
- **对外汇报以 `ensemble_metrics.json` / `ensemble_test_pred.conll` 为准**；单 seed 产物保留用于复核与消融分析。
- 本目录仅负责 Step 4b；跨模型最终汇总由 Step 5（pyt）统一处理。

---

## 9. 后续可能方向（若放宽约束）

当前解已触及"从头训练 + 无 test 泄漏 + 无预训练"这一约束集合的上限。如需继续逼近 mBERT（0.853）/ rule-based（1.0），只能引入破坏约束的手段：

1. 预训练词向量（FastText / GloVe 多语种版本）——会削弱与 mBERT 的「从头训练」对比定位。
2. 数据增广（同义词替换、回译）——课程数据集外的资源。
3. 允许规则后处理（hybrid）——会让 test 指标接近 rule-based 自身，失去模型评测意义。

对外工作已交付，`ensemble_metrics.json` 为最终版本。
