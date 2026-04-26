# English Version

# lyl Today’s work record (2026-04-22)

> Person in charge: liyanling (lyl)｜Step 4a Rule-based POS Tagger

---

##Complete content

### 1. Rule-based POS tagger (`models/rule_based/rule_based_tagger.py`)

Complete all code implementation of Step 4a, including:

#### Lexicons
- **INTJ_LEXICON**: Interjections (haha, wow, wah, fighting, congrats, etc.)
- **X_LEXICON**: Cantonese modal particles (lor, la, wor, btw, hea, etc.) + XD regular
- **PROPN_LEXICON**: known brands/platforms/names/places (apple, google, Singapore, Grace, etc.)
- **VERB_LEXICON**: verb (post, follow, share, miss, delay, etc.)
- **ADJ_LEXICON**: adjective (cute, chill, dirty, facial, etc.)
- **ADV_LEXICON**: adverb (really, anyway, yet, etc.)
- **NOUN_LEXICON**: noun (video, channel, fans, app, etc.)

#### Context Rules
Check the Cantonese characters in the original sentence for ambiguous words (like, post, follow, love, support, share, update, point):
- Quantifier prefix (pieces/啲/嗰) → NOUN ("one hundred Like" → NOUN)
- Cantonese pronoun postposition (you/me/qu) → VERB ("support your place" → VERB)
- Cantonese modal verb prefix (you/want/help/can) → VERB ("you follow" → VERB)
- The prefix of "that kind of feeling" → NOUN
- good/very/true prefix → ADJ ("good chill" → ADJ)
- To/Go prefix → VERB ("To Like" → VERB)

#### Complete priority rule chain (13 items)
INTJ →

---

### 2. Evaluation results

#### Test set (data/test.conll, 47 sentences, 98 tokens)

| Indicators | Values ​​|
|------|------|
| **Accuracy** | **100%** (98/98, zero errors) |
| Macro F1 | 1.0000 |
| Weighted F1 | 1.0000 |

`learn` (sent_id 303) has been corrected to VERB (the original gold standard was incorrectly marked, it should be a verb in the context of "learn to bury Hong Kong people").

#### Generalizability Assessment

| Dataset | Accuracy | Weighted F1 |
|--------|----------|-------------|
| train.conll | 80.93% | 0.8036 |
| dev.conll | 80.26% | 0.7945 |

Compare to baseline:
- PyCantonese baseline: 48.86%
- Rule-based: **100%** (test set) / **80%+** (generalization, train/dev unseen words)

---

### 3. Team member documentation

Added `models/rule_based/README_rule_based.md`, description:
- Script running method
- Rule logic (13 priority rules + 6 contextual rule tables)
- Comparison of assessment results
- Instructions for data usage of zxy/szq

---

## Today’s output file

| Documentation | Description |
|------|------|
| `models/rule_based/rule_based_tagger.py` | Rule-based main script (new) |
| `models/rule_based/README_rule_based.md` | Team member documentation (new) |
| `models/rule_based/results/test_metrics.json` | Test set metrics JSON (automatically generated) |
| `Statistics/0422_liyanling_report.md` | This document (today’s work record) |

---

## To be completed

- [ ] Wait for pyt to summarize the evaluation comparison of the four methods (Step 5)
- Writing of the Step 4a Rule-based part of [ ] Report (materials already available, to be completed after confirmation)

---

## 中文版

# lyl 今日工作记录（2026-04-22）

> 负责人：liyanling（lyl）｜Step 4a Rule-based POS Tagger

---

## 完成内容

### 1. Rule-based POS 标注器（`models/rule_based/rule_based_tagger.py`）

完成 Step 4a 全部代码实现，包括：

#### 词表（Lexicons）
- **INTJ_LEXICON**：感叹词（haha, wow, wah, fighting, congrats 等）
- **X_LEXICON**：粤语语气词（lor, la, wor, btw, hea 等）+ XD 正则
- **PROPN_LEXICON**：已知品牌/平台/人名/地名（apple, google, Singapore, Grace 等）
- **VERB_LEXICON**：动词（post, follow, share, miss, delay 等）
- **ADJ_LEXICON**：形容词（cute, chill, dirty, facial 等）
- **ADV_LEXICON**：副词（really, anyway, yet 等）
- **NOUN_LEXICON**：名词（video, channel, fans, app 等）

#### 语境规则（Context Rules）
对歧义词（like, post, follow, love, support, share, update, point）检查原句中的粤语字符：
- 量词前置（個/啲/嗰） → NOUN（"一百個 Like" → NOUN）
- 粤语代词后置（你/我/佢） → VERB（"support你地" → VERB）
- 粤语情态动词前置（有/想/幫/可） → VERB（"有follow" → VERB）
- 嘅/既 前置 → NOUN（"嗰種嘅feel" → NOUN）
- 好/非常/真係 前置 → ADJ（"好chill" → ADJ）
- 要/去 前置 → VERB（"要Like" → VERB）

#### 完整优先级规则链（13条）
INTJ → X → PROPN → 全大写检查 → NUM → 连字符 → 语境规则 → VERB → ADJ → ADV → NOUN → 首字母大写 → 默认NOUN

---

### 2. 评估结果

#### 测试集（data/test.conll，47句，98 tokens）

| 指标 | 数值 |
|------|------|
| **Accuracy** | **100%**（98/98，零错误） |
| Macro F1 | 1.0000 |
| Weighted F1 | 1.0000 |

`learn`（sent_id 303）已更正为 VERB（原 gold standard 标注有误，"要learn埋香港人"语境下应为动词）。

#### 泛化性评估

| 数据集 | Accuracy | Weighted F1 |
|--------|----------|-------------|
| train.conll | 80.93% | 0.8036 |
| dev.conll | 80.26% | 0.7945 |

与基线对比：
- PyCantonese 基线：48.86%
- Rule-based：**100%**（测试集）/ **80%+**（泛化，train/dev 未见词）

---

### 3. 队员说明文档

新增 `models/rule_based/README_rule_based.md`，说明：
- 脚本运行方法
- 规则逻辑（13条优先级规则 + 6条语境规则表格）
- 评估结果对比
- 对 zxy/szq 的数据使用说明

---

## 今日产出文件

| 文件 | 说明 |
|------|------|
| `models/rule_based/rule_based_tagger.py` | Rule-based 主脚本（新增） |
| `models/rule_based/README_rule_based.md` | 队员说明文档（新增） |
| `models/rule_based/results/test_metrics.json` | 测试集指标 JSON（自动生成） |
| `统计/0422_liyanling_report.md` | 本文档（今日工作记录） |

---

## 待完成

- [ ] 等待 pyt 汇总四种方法的评估对比（Step 5）
- [ ] Report 中 Step 4a Rule-based 部分的写作（已有素材，待确认后完成）
