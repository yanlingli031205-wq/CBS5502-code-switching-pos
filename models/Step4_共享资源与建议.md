# Step 4 共享资源与建议

> 为 BiLSTM-CRF (zxy) 和 mBERT (szq) 提供的经验总结  
> 作者：lyl (Step 4a Rule-based) | 日期：2026-04-22

---

## 一、数据协议（重要！）

为确保三种方法可对标比较，**请统一使用以下数据集**：

| 用途 | 文件路径 | 规模 | 用途 |
|------|---------|------|------|
| **训练** | `data/train.conll` | 216 句，388 tokens | BiLSTM-CRF / mBERT 训练 |
| **验证** | `data/dev.conll` | 46 句，76 tokens | 超参调参、早停 |
| **测试** | `data/test.conll` | 47 句，98 tokens | 最终性能评估（三种方法通用） |

**注意**：test.conll 中 sent_id 303 的 `learn` 已从 NOUN 改为 VERB（根据金标准纠错，语境"要learn埋香港人"）。

---

## 二、性能基准（Rule-based 结果）

### 2.1 baseline

| 指标 | 数值 |
|------|------|
| **Test 准确率** | **100%**（98/98） |
| **Train 准确率** | 80.93%（314/388） |
| **Weighted F1** | 0.80 |
| **vs PyCantonese** | +51.14% (test) / +32.07% (train) |

---

## 三、关键启示

### 3.1 粤英混码的特殊性

不能简单用通用英文 POS 标注器！6 条粤语语境规则是核心创新。

### 3.2 词汇表作为特征

7 个精心设计的词汇表可以被复用为：
- BiLSTM-CRF 的外部特征
- mBERT 微调时的预处理信号

### 3.3 错误分析的参考价值

Step 3 总结的 71 条 PyCantonese 错误直接指导了规则设计。

### 3.4 评估指标

注意 Macro F1 vs Weighted F1 的差异：
- **Macro F1**：少见词性拉低平均值
- **Weighted F1**：反映真实应用性能

---

## 四、最终结果汇总（所有方法已完成）

| 方法 | Test Acc | Weighted F1 | 状态 |
|------|---------|-------------|------|
| PyCantonese（基线） | 48.86% | ~0.49 | ✅ |
| **Rule-based**（lyl） | **100%** | **1.000** | ✅ 完成 |
| BiLSTM-CRF（zxy，目标 ≥0.82） | 80.61% | 0.7913 | ✅ 完成（2026-04-24） |
| mBERT（szq，目标 ≥0.83） | **90.82%** | **0.853** | ✅ 完成（2026-04-23） |

> **注**：Rule-based 100% 测试准确率在该数据集上存在过拟合风险（见 `统计/0424_项目阶段性结论.md`），训练集泛化性能为 80.93%。BiLSTM-CRF 与 mBERT 的 F1 差距约 0.06，考虑到 BiLSTM-CRF 从头训练、mBERT 带 110M 参数预训练权重，这是合理的结果。

---

## 五、共享资源

| 资源 | 位置 |
|------|------|
| **Rule-based 代码** | `models/rule_based/rule_based_tagger.py` |
| **Rule-based 文档** | `models/rule_based/README_rule_based.md` |
| **错误分析** | `统计/Step4a_Rule-based_方法报告.md` |
| **数据集** | `data/{train,dev,test}.conll` |

---

