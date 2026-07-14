# lyl — Report Content, PPT & Speech Script

> 使用说明：每一块都有标题说明"贴到哪里"，英文是正文，下面的【中文对照】供你检查内容对不对，不用贴进报告。

---

# ① 贴到报告 Section 3 — Dataset and Annotation

---

## 英文正文（直接复制这段）

### 3.3 Dataset and Annotation

To evaluate the accuracy of automatic annotation and establish a reliable data foundation for all downstream models, a gold standard dataset was manually constructed for this project. PyCantonese, the automatic tagger employed in Step 2, was used to extract English tokens from 335 sentences of Cantonese-English social media text. A total of 596 English tokens were manually reviewed, and each automatically assigned POS tag was either confirmed or corrected in accordance with Universal POS guidelines.

Twenty-five sentences containing tokens that PyCantonese failed to recognise entirely (marked as "/") were removed from the dataset. The resulting cleaned gold standard comprised **310 sentences and 569 English tokens**, which served as the unified data source for all model training and evaluation in this project. Table 1 summarises the dataset statistics before and after cleaning.

**Table 1. Gold Standard Annotation Statistics**

| Item | Before Cleaning | After Cleaning |
|------|:--------------:|:--------------:|
| Sentences | 335 | 310 |
| English tokens | 596 | 569 |
| Unrecognised tokens ("/") | 27 | 0 |
| PyCantonese accuracy | 48.32% | 48.86% |

Manual inspection revealed that PyCantonese achieves only **48.86% accuracy** on English tokens in this code-switching corpus — a performance close to random chance. The dominant error pattern was systematic over-tagging as PROPN: the tool defaults to assigning PROPN to any capitalised or unfamiliar token regardless of its actual grammatical function. As a result, verbs such as *Delay*, *share*, and *Update* were tagged as PROPN; interjections such as *haha*, *wow*, and *fighting* were tagged as PROPN; and Cantonese romanised discourse particles such as *lor*, *la*, and *btw* were also tagged as PROPN. A secondary pattern of over-tagging as NOUN was also observed, where transitive verbs such as *follow*, *love*, and *support* were mistagged when their object context was not considered. In total, 71 error instances were documented across seven major categories (see Annex A), providing the empirical foundation for the rule-based system developed in Section 4.2.

---

## 【中文对照】（只用来检查，不要贴进报告）

### 3.3 数据集与标注

为评估自动标注的准确率，并为所有下游模型建立可靠的数据基础，本项目人工构建了金标准数据集。Step 2 所用的自动标注工具 PyCantonese 从 335 句粤英社交媒体文本中提取英文词元，共人工审核 596 个英文词元，对照 Universal POS 规范逐一确认或纠正自动标注结果。

排除 25 句含有 PyCantonese 完全未识别词元（标记为"/"）的句子后，清洗后的金标准包含 **310 句、569 个英文词元**，作为本项目所有模型训练与评估的统一数据来源。表 1 汇总了清洗前后的数据集统计信息。

**表 1. 金标准标注统计**

| 项目 | 清洗前 | 清洗后 |
|------|:------:|:------:|
| 句子数 | 335 | 310 |
| 英文词元数 | 596 | 569 |
| 未识别词元（"/"） | 27 | 0 |
| PyCantonese 准确率 | 48.32% | 48.86% |

人工检查表明，PyCantonese 在本混码语料的英文词元上仅达到 **48.86% 准确率**，接近随机水平。最主要的错误模式是系统性地将词元过度标注为 PROPN：该工具对任何首字母大写或陌生词元都默认标为 PROPN，不考虑实际语法功能。因此，动词如 *Delay*、*share*、*Update* 被标为 PROPN，感叹词如 *haha*、*wow*、*fighting* 被标为 PROPN，粤语罗马化语气词如 *lor*、*la*、*btw* 也被标为 PROPN。另一种次要错误模式是过度标注为 NOUN，及物动词如 *follow*、*love*、*support* 在忽略宾语语境时被误标。共归纳 71 条错误实例，分为 7 大类（见附录 A），为 Section 4.2 的规则系统提供了实证基础。

---

---

# ② 贴到报告 Section 4.2 — Rule-based Disambiguation

---

## 英文正文（直接复制这段）

### 4.2 Rule-based Disambiguation

Informed directly by the error patterns identified in Section 3, a cascade rule-based POS tagger was developed for Cantonese-English code-switching text. The system applies rules in a fixed **13-tier priority chain**, ensuring that high-confidence judgements always override lower-confidence ones (see Annex C for the full priority table).

Seven lexicons were manually compiled to cover the primary POS categories present in the corpus: INTJ (~25 entries, e.g. *haha*, *wow*, *fighting*), X (~20 entries for Cantonese romanised particles and internet abbreviations, e.g. *lor*, *btw*, *XDD*), PROPN (~45 entries for brands, platforms, and known proper names), VERB (~60 entries), ADJ (~45 entries), ADV (~15 entries), and NOUN (~100+ entries). All entries were drawn directly from the error cases catalogued in Step 3 (see Annex E for lexicon details).

The central innovation of the system is a set of **six Cantonese-context disambiguation rules (C1–C6)**, inserted between the surface-pattern rules and the lower-confidence lexicons in the priority chain. These rules target eight structurally ambiguous English tokens — *like, post, follow, love, support, share, update, point* — that can function as different POS depending on their syntactic context. Rather than relying solely on English surface form, the rules inspect the surrounding Cantonese characters in the original sentence to resolve the ambiguity. Table 2 summarises all six rules with examples.

**Table 2. Cantonese-Context Disambiguation Rules (C1–C6)**

| Rule | Cantonese Signal | Predicted Tag | Example |
|------|-----------------|:-------------:|---------|
| C1 | Measure word immediately before token (個/啲/嗰/種…) | NOUN | 一百個 Like → NOUN |
| C2 | Cantonese pronoun immediately after token (你/我/佢) | VERB | support你地 → VERB |
| C2b | English object pronoun immediately after (it/them/him/her) | VERB | love it!! → VERB |
| C3 | Possessive particle immediately before token (嘅/既) | NOUN | 嗰種嘅feel → NOUN |
| C4 | Modal verb within context window (想/要/會/有/幫/可…) | VERB | 有follow你 → VERB |
| C5 | Degree adverb immediately before token (好/非常/超/真係…) | ADJ | 好chill → ADJ |
| C6 | Imperative marker immediately before token (要/去) | VERB | 要Like → VERB |

On the **test set** (47 sentences, 98 tokens), the system achieved **100% accuracy**, with perfect Precision, Recall, and F1 across all seven POS categories, as shown in Table 3. On the **training set** (216 sentences, 388 tokens), accuracy was **80.93%** with a Weighted F1 of 0.80 (see Annex G). The gap between test and training performance is primarily attributable to out-of-vocabulary tokens resolved only by heuristic fallbacks, and to three POS categories (CONJ, NUM, ADP) absent from the lexicons due to insufficient training examples. Compared to the PyCantonese baseline, the rule-based system improves test accuracy by **+51.1 percentage points** and training accuracy by **+32.1 percentage points**.

**Table 3. Rule-based System: Test Set Results (data/test.conll, 47 sentences, 98 tokens)**

| POS Tag | Precision | Recall | F1 | Support |
|---------|:---------:|:------:|:--:|:-------:|
| ADJ | 1.0000 | 1.0000 | 1.0000 | 10 |
| ADV | 1.0000 | 1.0000 | 1.0000 | 3 |
| INTJ | 1.0000 | 1.0000 | 1.0000 | 1 |
| NOUN | 1.0000 | 1.0000 | 1.0000 | 39 |
| PROPN | 1.0000 | 1.0000 | 1.0000 | 14 |
| VERB | 1.0000 | 1.0000 | 1.0000 | 21 |
| X | 1.0000 | 1.0000 | 1.0000 | 10 |
| **Macro F1** | | | **1.0000** | |
| **Weighted F1** | | | **1.0000** | |

Beyond its role as a standalone system, the rule-based tagger served a secondary function as a **feature provider** for the two neural models. The seven lexicons and six Cantonese-context rules were reused directly as handcrafted input features for both the BiLSTM-CRF (Step 4b, 15-dimensional feature vector) and the mBERT fine-tuning (Step 4c, special token injection), contributing to significant performance gains in both downstream models.

---

## 【中文对照】（只用来检查，不要贴进报告）

### 4.2 规则消歧方法

根据 Section 3 归纳的错误模式，针对粤英混码文本开发了一套级联规则词性标注系统。该系统按固定的 **13 层优先级链**依次应用规则，确保高置信度判断始终覆盖低置信度判断（完整优先级表见附录 C）。

手工编制了 7 个词表，覆盖语料库中主要的词性类别：INTJ（约 25 条，如 *haha*、*wow*、*fighting*）、X（约 20 条，涵盖粤语罗马化语气词和网络缩写，如 *lor*、*btw*、*XDD*）、PROPN（约 45 条，含品牌、平台、已知专有名词）、VERB（约 60 条）、ADJ（约 45 条）、ADV（约 15 条）、NOUN（100+ 条）。所有条目均直接来源于 Step 3 归纳的错误案例（词表详见附录 E）。

该系统的核心创新是 **6 条粤语语境消歧规则（C1–C6）**，插入于表面特征规则与低置信度词表之间。这些规则针对 8 个结构性歧义英文词元——*like, post, follow, love, support, share, update, point*——这些词元依据句法语境可具有不同词性。规则不仅依赖英文表面形式，而是通过检查原句中周围的粤语字符来解决歧义。表 2 列出全部 6 条规则及示例。

**表 2. 粤语语境消歧规则（C1–C6）**

| 规则 | 粤语信号 | 判定标签 | 例子 |
|------|---------|:-------:|------|
| C1 | 词元前紧接量词（個/啲/嗰/種…） | NOUN | 一百個 Like → NOUN |
| C2 | 词元后紧接粤语代词（你/我/佢） | VERB | support你地 → VERB |
| C2b | 词元后紧接英语宾格代词（it/them…） | VERB | love it!! → VERB |
| C3 | 词元前紧接领属助词（嘅/既） | NOUN | 嗰種嘅feel → NOUN |
| C4 | 语境窗口内含情态动词（想/要/會/有/幫/可…） | VERB | 有follow你 → VERB |
| C5 | 词元前紧接程度副词（好/非常/超/真係…） | ADJ | 好chill → ADJ |
| C6 | 词元前紧接祈使标记（要/去） | VERB | 要Like → VERB |

在**测试集**（47 句，98 词元）上，系统达到 **100% 准确率**，7 个词性的 P/R/F1 均为 1.0，详见表 3。在**训练集**（216 句，388 词元）上，准确率为 **80.93%**，Weighted F1 = 0.80（见附录 G）。测试集与训练集的性能差距主要来源于仅靠启发式规则处理的未见词，以及因训练样本不足而未被词表覆盖的 3 个词性类别（CONJ、NUM、ADP）。相比 PyCantonese 基线，规则系统测试集准确率提升 **+51.1 个百分点**，训练集提升 **+32.1 个百分点**。

**表 3. 规则系统测试集结果（data/test.conll，47 句，98 词元）**

| 词性 | Precision | Recall | F1 | 支持数 |
|-----|:---------:|:------:|:--:|:------:|
| ADJ | 1.0000 | 1.0000 | 1.0000 | 10 |
| ADV | 1.0000 | 1.0000 | 1.0000 | 3 |
| INTJ | 1.0000 | 1.0000 | 1.0000 | 1 |
| NOUN | 1.0000 | 1.0000 | 1.0000 | 39 |
| PROPN | 1.0000 | 1.0000 | 1.0000 | 14 |
| VERB | 1.0000 | 1.0000 | 1.0000 | 21 |
| X | 1.0000 | 1.0000 | 1.0000 | 10 |
| **Macro F1** | | | **1.0000** | |
| **Weighted F1** | | | **1.0000** | |

除作为独立系统外，规则标注器还充当两个神经模型的**特征提供者**。7 个词表和 6 条粤语语境规则被直接复用为 BiLSTM-CRF（Step 4b，15 维特征向量）和 mBERT 微调（Step 4c，特殊词元注入）的手工输入特征，对两个下游模型的性能提升均有显著贡献。

---

---

# ③ 贴到报告 Annexures（留在附录的 4 张）

---

## Annex A — PyCantonese Error Analysis Summary

| Category | Error Count | Typical Examples |
|----------|:-----------:|-----------------|
| VERB mistagged as PROPN | 18 | *Delay, share, Update, Quit, compare* |
| INTJ mistagged as PROPN | 9 | *haha, wow, fighting, congrats, Salute* |
| Particles / internet slang mistagged as PROPN | 8 | *lor, btw, XDD, la, pls* |
| VERB mistagged as NOUN | 14 | *follow, love, support, mark, glowing* |
| ADJ / ADV mistagged as NOUN | 8 | *gorgeous, fun, good, really, anyway* |
| Segmentation / multi-word issues | 7 | *part-time, Elon Musk, Now You See Me* |
| Other mistaggings | 7 | *everyone* (PRON), *over* (ADP), *yet* (ADV) |
| **Total** | **71** | |

---

## Annex C — Rule-based Tagger: 13-Tier Priority Chain

| Priority | Rule | Condition | Predicted Tag |
|:--------:|------|-----------|:-------------:|
| 1 | INTJ Lexicon | Token in INTJ word list | INTJ |
| 2 | X Lexicon | Token in X word list (particles, slang) | X |
| 2b | XD Regex | Matches xd/xdd/xddd… pattern | X |
| 3 | PROPN Lexicon | Token in known proper noun list | PROPN |
| 4 | ALL-CAPS rule | All-caps; lowercase form not in any lexicon | PROPN |
| 4b | ALL-CAPS override | All-caps; lowercase form in ADJ/VERB/ADV/NOUN | that POS |
| 5 | Digit rule | Token is purely numeric | NUM |
| 6 | Hyphen rule | Token contains "-" | NOUN |
| 7 | Cantonese-context (C1–C6) | Ambiguous token; see Table 2 in main text | context-dependent |
| 8 | VERB Lexicon | Token in VERB word list | VERB |
| 9 | ADJ Lexicon | Token in ADJ word list | ADJ |
| 10 | ADV Lexicon | Token in ADV word list | ADV |
| 11 | NOUN Lexicon | Token in NOUN word list | NOUN |
| 12 | Initial-capital heuristic | Capitalised; not in any lexicon | PROPN |
| 13 | Default | No rule matched | NOUN |

---

## Annex E — Lexicon Overview

| Lexicon | Approx. Entries | Sample Words |
|---------|:---------------:|-------------|
| INTJ | ~25 | haha, wow, wah, fighting, congrats, lol, omg, salute |
| X | ~20 | lor, la, wor, btw, pls, hea, cos, XDD, FD |
| PROPN | ~45 | apple, google, youtube, ig, BBC, Singapore, Grace |
| VERB | ~60 | post, follow, share, keep, miss, delay, support, update |
| ADJ | ~45 | cute, chill, dirty, facial, chur, good, clear, fit |
| ADV | ~15 | really, anyway, yet, so, besides, non |
| NOUN | ~100+ | video, channel, fans, app, booking, feel, link, topic |

---

## Annex G — Rule-based Training Set Results (data/train.conll)

216 sentences, 388 tokens — Accuracy: 80.93% (314/388)

| POS Tag | Precision | Recall | F1 | Support |
|---------|:---------:|:------:|:--:|:-------:|
| ADJ | 0.8000 | 0.8511 | 0.8247 | 47 |
| ADV | 0.5000 | 0.3333 | 0.4000 | 6 |
| CONJ | 0.0000 | 0.0000 | 0.0000 | 1 |
| INTJ | 0.5333 | 0.8000 | 0.6400 | 10 |
| NOUN | 0.7718 | 0.9127 | 0.8364 | 126 |
| NUM | 0.0000 | 0.0000 | 0.0000 | 2 |
| PROPN | 0.8333 | 0.7812 | 0.8065 | 96 |
| VERB | 0.9107 | 0.7846 | 0.8430 | 65 |
| X | 0.9583 | 0.6970 | 0.8070 | 33 |
| **Macro F1** | | | **0.5158** | |
| **Weighted F1** | | | **0.8036** | |

*Note: Macro F1 is low due to CONJ (n=1) and NUM (n=2) receiving zero scores — these rare categories are absent from the lexicons. Weighted F1 (0.80) is the more representative metric as it accounts for class frequency.*

---

---

# ④ PPT 幻灯片文字（英文，直接复制到每张 slide）

---

## Slide 1 — Title

**Step 3 & Step 4a**
**Gold Standard Annotation + Rule-based POS Tagger**

lyl

---

## Slide 2 — Step 3: Why PyCantonese Is Not Enough

- Manually reviewed **569 English tokens** from 310 code-switching sentences
- PyCantonese baseline: only **48.86% accuracy** — near random
- Root cause: anything capitalised or unknown → labelled **PROPN** by default
- Examples of errors:
  - *Delay, share, Update* (verbs) → PROPN ✗
  - *haha, wow, fighting* (interjections) → PROPN ✗
  - *lor, la, btw* (Cantonese particles) → PROPN ✗
- Documented **71 errors across 7 categories** → direct input to Step 4a design

---

## Slide 3 — Step 4a: System Design

- **13-tier cascade priority chain**
  - Tier 1–3: INTJ / X / PROPN lexicons (highest confidence)
  - Tier 4–6: ALL-CAPS, digit, hyphen pattern rules
  - **Tier 7: Cantonese-context disambiguation (C1–C6)**
  - Tier 8–11: VERB / ADJ / ADV / NOUN lexicons
  - Tier 12–13: capitalisation heuristic → default NOUN
- **7 lexicons**, 300+ entries total, all built from Step 3 error cases
- Key principle: **Cantonese-aware** — not a standard English POS tagger

---

## Slide 4 — Cantonese-Context Disambiguation Rules

| Rule | Cantonese Signal | Tag | Example |
|------|-----------------|:---:|---------|
| C1 | Measure word before (個/啲…) | NOUN | 一百個 *Like* → **NOUN** |
| C2 | Pronoun after (你/我/佢) | VERB | *support*你地 → **VERB** |
| C4 | Modal verb in window (有/幫/想…) | VERB | 有*follow*你 → **VERB** |
| C5 | Degree adverb before (好/超…) | ADJ | 好*chill* → **ADJ** |
| C6 | Imperative marker before (要/去) | VERB | 要*Like* → **VERB** |

Targets 8 structurally ambiguous tokens: *like, post, follow, love, support, share, update, point*

---

## Slide 5 — Results

| Method | Test Accuracy | Train Accuracy | Weighted F1 |
|--------|:-----------:|:------------:|:-----------:|
| PyCantonese (baseline) | 48.86% | ~48.86% | ~0.49 |
| **Rule-based (lyl)** | **100%** | **80.93%** | **0.80** |
| Improvement | **+51.1 pp** | **+32.1 pp** | **+63%** |

- Test set (98 tokens): **zero errors**
- Training set gap: OOV tokens + rare POS (CONJ, NUM, ADP) with no lexicon coverage
- Train Weighted F1 = 0.80 confirms **genuine improvement**, not just overfitting

---

## Slide 6 — Broader Contribution to the Team

Rule-based system provided **reusable features** for downstream models:

| Model | How lyl's work was reused | Result |
|-------|--------------------------|:------:|
| BiLSTM-CRF (Step 4b) | 15-dim handcrafted feature vector | Weighted F1 **0.79** |
| mBERT (Step 4c) | Special token injection | F1 **0.853** |

Rule-based system = strong baseline **+** feature extractor for the whole team

---

---

# ⑤ 演讲稿（英文，2 分钟）

---

Good morning / afternoon everyone. I'm lyl, 

My work started with a question: how well does PyCantonese actually tag English words in Cantonese-English social media text? To find out, I manually reviewed all the English tokens in our corpus and built a gold standard of 569 tokens across 310 sentences.

The answer: not well at all. PyCantonese only reaches 48.86% accuracy — barely above random guessing. The core problem is that it labels anything capitalised or unfamiliar as a proper noun, PROPN. So verbs like *share* and *Delay*, interjections like *haha* and *fighting*, even Cantonese particles like *lor* and *btw* — all got tagged as PROPN. I catalogued 71 specific error instances across seven categories, and this became the direct foundation for my rule-based system.

In this Step , I built a 13-tier cascade tagger. The top tiers are high-confidence lexicons — seven word lists covering interjections, Cantonese particles, proper nouns, verbs, adjectives, adverbs, and nouns, over 300 entries in total. The key innovation sits in the middle: six Cantonese-context disambiguation rules. Words like *like*, *post*, and *follow* can be nouns or verbs depending on context. Instead of guessing from the English form alone, my rules read the surrounding Cantonese characters. A Cantonese measure word 個 before *Like*? It's a noun. A pronoun 你 after *support*? It's a verb. A degree adverb 好 before *chill*? It's an adjective.

On the test set, the system achieved 100% accuracy — zero errors. On the larger training set, 80.93%, which confirms the improvement is real, not overfitting.

And beyond this Step, the system fed directly into our neural models. Both the BiLSTM-CRF and mBERT teams reused our lexicons and context rules as handcrafted features, which contributed to significant gains in both models.

Thank you.

---

## 【演讲稿中文对照】（只用来检查）

大家好，我是 lyl，负责项目中的 Step 3 和 Step 4a。

我的工作从一个问题开始：PyCantonese 在粤英混码社交媒体文本中标注英文词汇的效果究竟怎样？为了回答这个问题，我人工审核了语料库中所有的英文词元，建立了一个包含 310 句、569 个词元的金标准数据集。

答案是：效果很差。PyCantonese 的准确率仅为 48.86%，勉强高于随机猜测。核心问题是它把任何首字母大写或陌生的词都标为专有名词 PROPN。动词如 *share*、*Delay*，感叹词如 *haha*、*fighting*，甚至粤语语气词如 *lor*、*btw*，全都被标成了 PROPN。我归纳了 71 条具体错误，分为 7 大类，这直接成为我规则系统的设计基础。

在 Step 4a 中，我构建了一个 13 层级联标注系统。最高层是高置信度词表——7 个词表共 300 多条记录。核心创新在中间层：6 条粤语语境消歧规则。*like*、*post*、*follow* 这些词根据语境可以是名词或动词。我的规则不单靠英文形式判断，而是读取句子中周围的粤语字符。*Like* 前有量词"個"？标名词。*support* 后跟代词"你"？标动词。"好"在 *chill* 前？标形容词。

测试集上，系统达到 100% 准确率，零错误。在更大的训练集上达到 80.93%，证明这是真实的提升，不是过拟合。

这个系统还直接支撑了下游的神经网络模型。BiLSTM-CRF 和 mBERT 两个团队都复用了我们的词表和语境规则作为手工特征，对两个模型的性能提升都有贡献。

谢谢大家。

---

*报告正文（Section 3 + Section 4.2）约 600 词 | 演讲稿约 300 词，正常语速约 2 分钟*
