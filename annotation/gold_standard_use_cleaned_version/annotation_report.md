# Gold Standard Annotation Report

## 数据概览

| 项目 | 数值 |
|------|------|
| 总句子数 | 335 |
| 总英文 token 数（含 `/`） | 623 |
| 其中标注为 `/` 的 token 数 | 27 |
| `/` 占比（token 级别） | 4.33% |

> **说明**：`/` 表示 PyCantonese 未能识别该英文 token，即该词在自动标注中完全缺失。

---

## 清洗说明

移除含有任意 `/` 标注的句子（共 25 句），得到 `gold_standard_cleaned.csv`：

| 项目 | 清洗前 | 清洗后 |
|------|--------|--------|
| 句子数 | 335 | 310 |
| 英文 token 数 | 596 | 569 |

---

## PyCantonese 自动标注正确率

### 清洗前（含所有可评估 token，排除 `/`）

| 项目 | 数值 |
|------|------|
| 可评估 token 数 | 596 |
| 标注正确数 | 288 |
| 标注错误数 | 308 |
| **正确率** | **48.32%** |

### 清洗后（gold_standard_cleaned.csv）

| 项目 | 数值 |
|------|------|
| 可评估 token 数 | 569 |
| 标注正确数 | 278 |
| 标注错误数 | 291 |
| **正确率** | **48.86%** |

---

## NER 引入的改进与局限

pyt 在 v2 版本中引入 spaCy NER，相较于早期纯 PyCantonese 版本有明显改进：

**改进之处：**
- v1 版本无法识别连续多个英文词（如 `Elon Musk`、`Donald Trump`、`final fantasy`），仅标注首词，后续词漏提取
- v2 引入 NER 后，多词实体可被完整识别并标为 `PROPN`，如 `Elon Musk`、`BBC`、`Iron Man` 等专有名词识别准确率明显提升

**仍存在的局限：**
- NER 优先策略会将部分普通英文词误判为实体，过度标注为 `PROPN`（如 `facial`、`fans`、`feel`、`Delay` 等）
- 这是本项目 rule-based / BiLSTM-CRF / mBERT 三种方法需要重点改进的方向

---

## 主要发现

PyCantonese 在粤英混码（Cantonese-English code-switching）语料上的英文词性标注正确率仅约 **48.86%**，接近随机水平，主要错误类型包括：

| 错误类型 | 典型案例 |
|---------|---------|
| `VERB_as_PROPN` | Delay, Quit, compare, like, share |
| `ADJ_as_PROPN` | Huge, Dramatic, Chill |
| `INTJ_as_PROPN` | haha, lol, omg |
| `X_as_PROPN` | btw, XDD, anyway |
| `NOUN_as_PROPN` | facial, fans, feel, BGM, MC, MV |
| `VERB_as_NOUN` | follow, love, point, cam, channel |
| `ADJ_as_NOUN` | gorgeous, native |
| `ADV_as_NOUN` | besides, non, casino |
| `NOUN_as_ADJ` | mic, travel, base |
| `PRON_as_NOUN` | everyone |
| `ADP_as_NOUN` | over |

**核心问题**：PyCantonese 并非为英文词性标注设计，在处理混码语境中的英文 token 时，倾向于将首字母大写或不认识的词默认标为 `PROPN`，导致系统性误标。

---

## 文件说明

| 文件 | 说明 |
|------|------|
| `gold_standard_completed.csv` | 完整人工标注结果（含 `/` 行） |
| `gold_standard_cleaned.csv` | 清洗后数据（移除含 `/` 的句子，供模型训练与评估使用） |

> **⚠️ 致队友（zxy / szq）：请使用 `gold_standard_cleaned.csv` 作为后续所有模型训练与评估的数据来源，勿使用 `gold_standard_completed.csv`。**
