# English Version

# Gold Standard Annotation Report

## Data Overview

| Item | Value |
|------|------|
|Total number of sentences | 335 |
| Total number of English tokens (including `/`) | 623 |
| The number of tokens marked `/` | 27 |
| `/` Proportion (token level) | 4.33% |

> **Explanation**: `/` means that PyCantonese fails to recognize the English token, that is, the word is completely missing in the automatic annotation.

---

## Cleaning Instructions

Remove sentences containing any `/` mark (25 sentences in total) and get `gold_standard_cleaned.csv`:

| Project | Before Cleaning | After Cleaning |
|------|--------|--------|
| Number of sentences | 335 | 310 |
| English token number | 596 | 569 |

---

## PyCantonese automatic annotation accuracy rate

### Before cleaning (including all evaluable tokens, excluding `/`)

| Item | Value |
|------|------|
| Number of evaluable tokens | 596 |
| Mark the correct number | 288 |
| Number of annotation errors | 308 |
| **Correct rate** | **48.32%** |

### After cleaning (gold_standard_cleaned.csv)

| Item | Value |
|------|------|
| Number of evaluable tokens | 569 |
| Mark the correct number | 278 |
| Number of annotation errors | 291 |
| **Correct rate** | **48.86%** |

---

## Improvements and limitations introduced by NER

pyt introduced spaCy NER in the v2 version, which is significantly improved compared to the early pure PyCantonese version:

**Improvements:**
- The v1 version cannot recognize multiple consecutive English words (such as `Elon Musk`, `Donald Trump`, `final fantasy`), only the first word is marked, and subsequent words are not extracted.
- After the introduction of NER in v2, multi-word entities can be fully recognized and marked as `PROPN`, and the recognition accuracy of proper nouns such as `Elon Musk`, `BBC`, `Iron Man` and so on has been significantly improved.

**Remaining limitations:**
- The NER priority strategy will misjudge some common English words as entities and over-annotate them as `PROPN` (such as `facial`, `fans`, `feel`, `Delay`, etc.)
- This is the direction in which the three methods of rule-based / BiLSTM-CRF / mBERT need to be improved in this project

---

## Main findings

The accuracy rate of PyCantonese's English part-of-speech tagging on the Cantonese-English code-switching corpus is only about **48.86%**, which is close to the random level. The main error types include:

| Error types | Typical cases |
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

**Core issue**: PyCantonese is not designed for English part-of-speech tagging. When processing English tokens in mixed-coding contexts, it tends to mark words with capital letters or unfamiliar words as `PROPN` by default, resulting in systematic mislabeling.

---

## File description

| Documentation | Description |
|------|------|
| `gold_standard_completed.csv` | Complete manual annotation results (including `/` lines) |
| `gold_standard_cleaned.csv` | Cleaned data (remove sentences containing `/` for model training and evaluation) |

> **⚠️ To teammates (zxy / szq): Please use `gold_standard_cleaned.csv` as the data source for all subsequent model training and evaluation. Do not use `gold_standard_completed.csv`. **

---

## 中文版

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
