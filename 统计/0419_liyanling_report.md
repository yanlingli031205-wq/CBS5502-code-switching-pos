# lyl 标注贡献整理（供报告写作参考）
> 日期：2026-04-19｜负责人：lyl（Step 3 人工标注 Gold Standard + Step 4a Rule-based）

---

## 一、数据集基本统计

| 项目 | 数值 |
|------|------|
| 总句子数 | 335 |
| 含英文 token 的句子数 | 323（96.4%） |
| 总 token 数 | 5,891 |
| 英文 token 数 | 603（占 10.2%） |
| NER 阶段贡献的英文 token 数 | 120 |

> 数据来源：pyt 产出的 `corpus/outputs_ner_spacy/dataset_stats.json`

---

## 二、Gold Standard 标注统计

### 2.1 人工标注规模

| 项目 | 数值 |
|------|------|
| 人工标注句子数 | 335 |
| 人工标注英文 token 数（含 `/`） | 623 |
| 标注为 `/`（PyCantonese 未识别）的 token 数 | 27 |
| `/` 占比（token 级别） | 4.33% |
| 清洗后句子数（gold_standard_cleaned.csv） | 310 |
| 清洗后英文 token 数 | 569 |

> `/` 表示 PyCantonese 未能提取该英文 token，该词在自动标注中完全缺失。含 `/` 的句子（共 25 句）已从 cleaned 版本中移除。

### 2.2 标注规范

人工标注采用 Universal POS Tags 标准，共 12 个标签：

| 标签 | 含义 | 典型例子 |
|------|------|---------|
| NOUN | 普通名词 | video, mic, feel, support |
| PROPN | 专有名词 | Tesla, Elon Musk, YouTube |
| VERB | 动词 | post, claim, follow, update |
| ADJ | 形容词 | cool, huge, cute |
| ADV | 副词 | really, so, yet, besides |
| NUM | 数词 | one, 100 |
| PRON | 代词 | I, you, everyone |
| DET | 限定词 | the, a, this |
| ADP | 介词 | in, for, over |
| CONJ | 连词 | and, but, or |
| INTJ | 感叹词 | haha, omg, congrats, wah |
| X | 无法分类 | btw, lol, XDD, pls |

---

## 三、PyCantonese 自动标注正确率

### 3.1 总体正确率

| 数据集 | Token 数 | 正确数 | 错误数 | 正确率 |
|--------|---------|--------|--------|--------|
| 全部（排除 `/`） | 596 | 288 | 308 | 48.32% |
| 清洗后（cleaned） | 569 | 278 | 291 | **48.86%** |

> PyCantonese 在粤英混码语境下的英文 POS 标注正确率约为 **48.86%**，接近随机水平，表明该工具并未针对 code-switching 场景优化。

### 3.2 错误归因

PyCantonese 的主要系统性错误为 **PROPN 过度标注**：遇到首字母大写或不认识的英文词时，默认标为 PROPN。这一问题在引入 spaCy NER 后有所改善（多词人名/品牌名识别更准），但 NER-first 策略同时带来了新的 PROPN 误标问题。

---

## 四、主要错误类型及频次

以下为人工标注过程中发现的主要错误类型，共归纳 71 条，涵盖以下 5 大类：

| 错误类型 | 典型案例 | 说明 |
|---------|---------|------|
| `VERB_as_PROPN` | Delay, Quit, share, Update, compare | 首字母大写动词被误判为专有名词 |
| `ADJ_as_PROPN` | Huge, Dramatic, Chill, Nice, cute | 首字母大写形容词被误判为专有名词 |
| `INTJ_as_PROPN` | haha, lol, omg, wow, congrats, Salute | 感叹词被误判为专有名词 |
| `X_as_PROPN` | btw, XDD, pls, wor, lor | 网络缩写/语气词被误判为专有名词 |
| `NOUN_as_PROPN` | facial, fans, BGM, MC, MV, feel, po | 普通名词被误判为专有名词 |
| `VERB_as_NOUN` | looks, point, follow, love, made, support, glowing, mark, update | 动词被误判为名词 |
| `ADJ_as_NOUN` | gorgeous, native, fun, good, fit, better, clear | 形容词被误判为名词 |
| `ADV_as_NOUN` | non, so, really, anyway | 副词被误判为名词 |
| `NOUN_as_ADJ` | Travel, Mic, base, ball, topic, details, link, logic, lip, feel | 名词被误判为形容词 |
| `VERB_as_ADJ` | mute, update, inspired, appreciate | 动词被误判为形容词 |
| `ADJ_as_VERB` | proud, inspiring | 形容词被误判为动词 |
| `NOUN_as_VERB` | channel, team | 名词被误判为动词 |
| `PROPN_as_NOUN` | YouTube, threads, ig, YouTuber, 部分人名/店名 | 专有名词被误判为普通名词 |
| `NOUN_as_ADV` | Lunch, casino | 名词被误判为副词 |
| `ADP_as_NOUN` | over（voice over） | 介词被误判为名词 |
| `ADV_as_VERB` | yet | 副词被误判为动词 |
| `ADV_as_ADJ` | much（so much） | 副词被误判为形容词 |
| `PRON_as_NOUN` | everyone | 代词被误判为名词 |

> 详细错误分析见 `annotation/error_analysis/error_analysis_report.md`

---

## 五、Rule-based 修正方向（Step 4a 初步规则）

基于错误分析，拟定以下消歧规则：

| 规则编号 | 规则描述 |
|---------|---------|
| R1 | 建立常见英文动词词表，若 token 在词表中且 auto_pos == PROPN → 改为 VERB |
| R2 | 建立常见英文形容词词表，若 token 在词表中且 auto_pos == PROPN → 改为 ADJ |
| R3 | 建立感叹词词表（haha, lol, omg, wow, congrats, fighting 等），auto_pos 非 INTJ → 改为 INTJ |
| R4 | 建立网络缩写/语气词词表（btw, pls, XD, XDD, wor, lor, ar, la 等）→ 改为 X |
| R5 | token 全小写且 auto_pos == PROPN → 进一步判断词性 |
| R6 | follow/support/share 前有人称代词或人名作主语 → 改为 VERB |
| R7 | feel 前有"嘅"或动词 → 改为 NOUN |
| R8 | 動詞"說/講"后接英文词 → 优先标 NOUN |
| R9 | love 后紧接代词（it/them 等）→ 改为 VERB |
| R10 | 多个连续首字母大写词 → 整体识别为 PROPN |
| R11 | 含连字符的词（如 part-time）→ 不拆分，整体标 NOUN |
| R12 | "D" 用作粤语"的"替代时 → 标 X，不计英文 token |
| R13 | 数字 token → 标 NUM |
| R14 | 前接副词 → 后接词倾向 VERB；前接数词 → 后接词倾向 NOUN |

---

## 六、可写入报告的关键结论

1. PyCantonese 在粤英混码语料上的英文 POS 自动标注正确率仅约 **48.86%**，接近随机基线，体现了该工具在 code-switching 场景下的局限性。

2. 最主要的系统性错误为 **PROPN 过度标注**：PyCantonese 倾向于将大写或不认识的英文词默认标为 PROPN，在 71 条归纳的错误中，涉及 PROPN 误标的超过半数。

3. 引入 spaCy NER 后（v2），多词专有名词（如 Elon Musk、BBC）的识别准确率有所提升，但 NER-first 策略同时引入了新的普通词 PROPN 误标问题，两者存在 trade-off。

4. 粤英混码中的英文词存在大量语境依赖的词性歧义（如 post/feel/support/update 在不同句子中词性不同），这正是 rule-based、BiLSTM-CRF、mBERT 三种方法需要解决的核心挑战。

5. PyCantonese 无法识别的英文 token（标注为 `/`）占总 token 的 **4.33%**，说明自动提取阶段本身存在漏识别问题，进一步影响了下游标注质量。
