# PyCantonese 标注错误分析报告 / PyCantonese Annotation Error Analysis Report

---

# 中文版

## 一、PROPN 过度标注

### 1.1 首字母大写词被误判为 PROPN

PyCantonese 倾向于将首字母大写或全大写的英文词默认标为 PROPN，即使其实际词性并非专有名词。

- **#1** Hello（应为 VERB），Delay（应为 VERB，例：慣性Delay），Quit（应为 VERB，例：Quit左佢囉），Aunty（应为 NOUN），Huge（应为 ADJ），Dramatic（应为 ADJ）
- **#11** Chill（应为 ADJ）被误判为 PROPN
- **#18** Besides（应为 ADV）被误判，句首且首字母大写，合理怀疑是大写触发误判
- **#66** Update（应为 VERB）被误判为 PROPN，例：IG 都無咩Update
- **#70** Nice（应为 ADJ），cute（应为 ADJ）被误判为 PROPN

### 1.2 普通名词被误判为 PROPN

- **#2** facial、fans、part、FEEL（全大写）、best 被误判为 PROPN
- **#51** BGM、MC、MV、feel 被误判为 PROPN（应为 NOUN）
- **#53** view（例：夠十萬view）被误判为 PROPN（应为 NOUN）
- **#69** post 的缩写 "po"（如 "po主"）被误判为 PROPN

### 1.3 动词被误判为 PROPN

- **#2** subscribed 被误判为 PROPN
- **#40** compare、like 被误判为 PROPN（应为 VERB）
- **#45** 路過、Subscribed、LIKE（首字母或全大写）被误判为 PROPN
- **#53** share 被误判为 PROPN，例：幫手share出去（share 应为 VERB）
- **#66** Update 被误判为 PROPN，例：IG 都無咩Update（应为 VERB）

### 1.4 感叹词被误判为 PROPN

- **#46** haha、lol、omg、omgggg、fighting、wow、congrats 均被误判为 PROPN（应为 INTJ）
- **#50** 例句"叻女！敬禮！Salute!"中，几乎所有词都被误判为 PROPN（Salute 应为 INTJ）

### 1.5 网络缩写词/语气词被误判为 PROPN

- **#4** XDDDDD、XDD（网络表情词）被误判为 PROPN（应为 X）
- **#41** btw、pls、wor、lor、ar、la 被误判为 PROPN（应为 X）
- **#13** Btw、anyway 有时被误判为 PROPN（应为 X 或 ADV）

---

## 二、NOUN 过度标注

### 2.1 动词被误判为 NOUN

- **#5** looks（第三人称单数动词形式）被误判为 NOUN
- **#8** point 被误判为 NOUN，例：霓虹妹的point下睫毛（应为 VERB）
- **#19** follow 被误判为 NOUN，例：一直都有follow（应为 VERB）
- **#29** love 被误判为 NOUN，例：love it!!（后接宾语，应为 VERB）
- **#38** cam（后面出现"影片/影"时应为 VERB），fly（例：fly去德国），follow 被误判为 NOUN
- **#55** made（过去式动词）、support、share、propose、support（例：support你地）被误判为 NOUN
- **#64** glowing（例：能看出来你整个人都在glowing）、mark（例：你突然mark個標籤出來）被误判为 NOUN
- **#67** update 被误判为 NOUN（应为 VERB）

### 2.2 形容词被误判为 NOUN

- **#39** gorgeous 被误判为 NOUN（应为 ADJ）
- **#48** native（例：non native speaker 中的 native）被误判为 NOUN（应为 ADJ）
- **#56** fun、good、fit、better、clear 被误判为 NOUN（应为 ADJ）

### 2.3 副词被误判为 NOUN

- **#47** non（例：non native speaker 中的 non）被误判为 NOUN（应为 ADV）；so（例：so happy 中的 so）被误判为 NOUN（应为 ADV）
- **#54** really、anyway 被误判为 NOUN（应为 ADV）

### 2.4 代词被误判为 NOUN

- **#42** everyone 被误判为 NOUN（应为 PRON）

### 2.5 专有名词被误判为普通名词 NOUN

- **#14** 部分香港店名（专有名词）被误判为普通名词 NOUN
- **#16** 人名（PROPN）被误判为 NOUN
- **#25** YouTuber 被误判为 NOUN（应为 PROPN）
- **#37** YouTube、threads、ig 被误判为 NOUN（应为 PROPN）

---

## 三、误判为 ADJ

### 3.1 名词被误判为 ADJ

- **#17** Travel 被误判为 ADJ（应为 NOUN）
- **#23** Mic（麦克风）被误判为 ADJ（应为 NOUN），例：有佩戴mic吗
- **#35** base（例：Gundam base）、ball 被误判为 ADJ（应为 NOUN）
- **#43** like 被误判为 ADJ，例：点like（like 在此为 NOUN）
- **#59** topic 被误判为 ADJ（应为 NOUN）
- **#62** details 被误判为 ADJ（应为 NOUN）
- **#65** link（例：可以分享連身裙link？）、logic（例：佢會用番中文既logic去講廣東話）被误判为 ADJ（应为 NOUN）
- **#68** lip（例：同你支lip stick 的 lip）被误判为 ADJ（应为 NOUN）
- **#71** feel（例：串燒店嗰度...已經有嗰種feel啦）被误判为 ADJ（应为 NOUN）

### 3.2 动词被误判为 ADJ

- **#52** mute 被误判为 ADJ，例：真係好想mute聲（应为 VERB）
- **#57** update（例：update vlog 中的 update）、inspired（动词过去式）、appreciate 被误判为 ADJ（应为 VERB）

### 3.3 副词被误判为 ADJ

- **#58** much 被误判为 ADJ，例：so much 中的 much（应为 ADV）

---

## 四、误判为 VERB

### 4.1 形容词被误判为 VERB

- **#33** 英文常见形容词被错标为 VERB
- **#36** proud 被误判为 VERB（应为 ADJ）
- **#61** inspiring 被误判为 VERB（应为 ADJ）

### 4.2 名词被误判为 VERB

- **#44** post 被误判为 VERB，例：係threads經常睇到羊人既post（此处 post 为 NOUN，应为名词）
- **#49** channel（两次均误判）、team 被误判为 VERB（应为 NOUN）

### 4.3 副词被误判为 VERB

- **#60** yet 被误判为 VERB，例：the best is yet to come（应为 ADV）

### 4.4 动名词被误判为 VERB

- **#63** 动名词会被误判为 VERB，例：propose planning 中的 planning（应为 NOUN）

---

## 五、误判为其他词性

### 5.1 名词被误判为 ADV

- **#12** Lunch（应为 NOUN）被误判为 ADV
- **#27** casino（应为 NOUN，意为赌场）被误判为 ADV，例：唯一一個知道第一個反應係casino

### 5.2 介词被误判为 NOUN

- **#24** over（应为 ADP/介词）被误判为 NOUN，例：voice over 中的 over

### 5.3 特殊词性误判

- **#3** up 被误判为 VERB，但 up 在此语境下实际无动词词性
- **#7** like 被误判为 ADJ，但 like 只有 NOUN 和 VERB 两种词性
- **#10** wah（感叹词 INTJ）被误判为 NOUN，例：wah 真係好靚

---

## 六、分词与识别问题

### 6.1 多词专有名词处理不当

- **#6** 连续英文词有时被全部标为 NOUN
- **#20** 多个专有名词被拆分，每个词单独标 PROPN，例：Bakehouse蛋撻的撻底是酸種Sourdough Eggs Tart
- **#26** 部分香港店名识别不准，例：Vission Bakery、Bake House
- **#30** 多个连续首字母大写英文词应整体识别为专有名词，例：Now You See Me、House Keeping、Drag Queen

### 6.2 特定词汇识别问题

- **#9** "po主"中 po 是 post 的缩写，应视为专有名词/名词
- **#22** feel 在不同句子中词性不同，容易被错标：前面有"嘅"或前面是动词时，feel 应标 NOUN（例：爹哋講廣東話有倪匡先生嘅feel）
- **#15** 部分产品名标注正确（PROPN），但标注行为前后不一致
- **#21** daddy、mom、uncle、mami、dad 等亲属称谓识别错误
- **#31** "D" 表示粤语"的"时，应标 X，不识别为英文 token
- **#32** 数字应标 NUM
- **#34** part-time 整体为 NOUN，建议不拆分处理

---

## 七、规则建议

- **#19 follow 规则**：follow 前面有人称代词或人名作主语 → 标 VERB
- **#22 feel 规则**：feel 前面有"嘅"或前面是动词 → feel 标 NOUN
- **#28 "说"字规则**：說/講 后接英文词 → 优先标 NOUN，例：說romansh
- **#29 love 规则**：love 后面紧接代词（it / them 等）→ 标 VERB
- **#30 连续大写规则**：多个连续首字母大写英文词 → 整体标 PROPN
- **#34 复合词规则**：含连字符的词（如 part-time）→ 不拆分，整体标 NOUN
- **#53 上下文规则**：前面是副词 → 后接词标 VERB；前面是数词 → 后接词标 NOUN

---

## 八、PyCantonese 改进说明（pyt v2）

v2 版本引入 spaCy NER，相较 v1 有以下改进：

- v1 无法识别连续多词英文（如 Elon Musk 只识别 Elon，后续词漏提取）；v2 加入 NER 后可整体识别多词实体
- BBC、Elon Musk 等人名/机构名可被正确识别为 PROPN
- 局限：NER 优先策略有时将普通词过度标注为 PROPN

---
---

# English Version

## 1. Over-tagging as PROPN

### 1.1 Capitalized Words Mistagged as PROPN

PyCantonese tends to default to PROPN for words beginning with a capital letter or written in all-caps, even when the actual POS is not a proper noun.

- **#1** Hello (→VERB), Delay (→VERB, e.g. 慣性Delay), Quit (→VERB, e.g. Quit左佢囉), Aunty (→NOUN), Huge (→ADJ), Dramatic (→ADJ)
- **#11** Chill (→ADJ) mistagged as PROPN
- **#18** Besides (→ADV) mistagged; sentence-initial position with capital letter likely triggers PROPN
- **#66** Update (→VERB) mistagged as PROPN, e.g. IG 都無咩Update
- **#70** Nice (→ADJ), cute (→ADJ) mistagged as PROPN

### 1.2 Common Nouns Mistagged as PROPN

- **#2** facial, fans, part, FEEL (all-caps), best mistagged as PROPN
- **#51** BGM, MC, MV, feel mistagged as PROPN (should be NOUN)
- **#53** view (e.g. 夠十萬view) mistagged as PROPN (should be NOUN)
- **#69** Abbreviation "po" (short for post, as in "po主") mistagged as PROPN

### 1.3 Verbs Mistagged as PROPN

- **#2** subscribed mistagged as PROPN
- **#40** compare, like mistagged as PROPN (should be VERB)
- **#45** 路過, Subscribed, LIKE (capitalized/all-caps) mistagged as PROPN
- **#53** share mistagged as PROPN, e.g. 幫手share出去 (should be VERB)
- **#66** Update mistagged as PROPN, e.g. IG 都無咩Update (should be VERB)

### 1.4 Interjections Mistagged as PROPN

- **#46** haha, lol, omg, omgggg, fighting, wow, congrats mistagged as PROPN (should be INTJ)
- **#50** In "叻女！敬禮！Salute!", nearly all tokens mistagged as PROPN (Salute should be INTJ)

### 1.5 Internet Slang / Discourse Particles Mistagged as PROPN

- **#4** XDDDDD, XDD (internet emoticons) mistagged as PROPN (should be X)
- **#41** btw, pls, wor, lor, ar, la mistagged as PROPN (should be X)
- **#13** Btw, anyway sometimes mistagged as PROPN (should be X or ADV)

---

## 2. Over-tagging as NOUN

### 2.1 Verbs Mistagged as NOUN

- **#5** looks (3rd person singular verb form) mistagged as NOUN
- **#8** point mistagged as NOUN, e.g. 霓虹妹的point下睫毛 (should be VERB)
- **#19** follow mistagged as NOUN, e.g. 一直都有follow (should be VERB)
- **#29** love mistagged as NOUN, e.g. love it!! (followed by object, should be VERB)
- **#38** cam (should be VERB when followed by 影片/影), fly (e.g. fly去德国), follow mistagged as NOUN
- **#55** made (past tense verb), support, share, propose, support (e.g. support你地) mistagged as NOUN
- **#64** glowing (e.g. 能看出来你整个人都在glowing), mark (e.g. 你突然mark個標籤出來) mistagged as NOUN
- **#67** update mistagged as NOUN (should be VERB)

### 2.2 Adjectives Mistagged as NOUN

- **#39** gorgeous mistagged as NOUN (should be ADJ)
- **#48** native (in non native speaker) mistagged as NOUN (should be ADJ)
- **#56** fun, good, fit, better, clear mistagged as NOUN (should be ADJ)

### 2.3 Adverbs Mistagged as NOUN

- **#47** non (in non native speaker) mistagged as NOUN (should be ADV); so (in so happy) mistagged as NOUN (should be ADV)
- **#54** really, anyway mistagged as NOUN (should be ADV)

### 2.4 Pronouns Mistagged as NOUN

- **#42** everyone mistagged as NOUN (should be PRON)

### 2.5 Proper Nouns Mistagged as Common NOUN

- **#14** Some Hong Kong store names (proper nouns) mistagged as NOUN
- **#16** Personal names (PROPN) mistagged as NOUN
- **#25** YouTuber mistagged as NOUN (should be PROPN)
- **#37** YouTube, threads, ig mistagged as NOUN (should be PROPN)

---

## 3. Mistagged as ADJ

### 3.1 Nouns Mistagged as ADJ

- **#17** Travel mistagged as ADJ (should be NOUN)
- **#23** Mic mistagged as ADJ (should be NOUN), e.g. 有佩戴mic吗
- **#35** base (e.g. Gundam base), ball mistagged as ADJ (should be NOUN)
- **#43** like mistagged as ADJ, e.g. 点like (like is NOUN here)
- **#59** topic mistagged as ADJ (should be NOUN)
- **#62** details mistagged as ADJ (should be NOUN)
- **#65** link (e.g. 可以分享連身裙link？), logic (e.g. 佢會用番中文既logic去講廣東話) mistagged as ADJ (should be NOUN)
- **#68** lip (e.g. 同你支lip stick 的 lip) mistagged as ADJ (should be NOUN)
- **#71** feel (e.g. 串燒店嗰度...已經有嗰種feel啦) mistagged as ADJ (should be NOUN)

### 3.2 Verbs Mistagged as ADJ

- **#52** mute mistagged as ADJ, e.g. 真係好想mute聲 (should be VERB)
- **#57** update (in update vlog), inspired (past tense verb), appreciate mistagged as ADJ (should be VERB)

### 3.3 Adverbs Mistagged as ADJ

- **#58** much mistagged as ADJ, e.g. so much (should be ADV)

---

## 4. Mistagged as VERB

### 4.1 Adjectives Mistagged as VERB

- **#33** Common English adjectives mistagged as VERB
- **#36** proud mistagged as VERB (should be ADJ)
- **#61** inspiring mistagged as VERB (should be ADJ)

### 4.2 Nouns Mistagged as VERB

- **#44** post mistagged as VERB, e.g. 係threads經常睇到羊人既post (post is NOUN here)
- **#49** channel (mistagged twice), team mistagged as VERB (should be NOUN)

### 4.3 Adverbs Mistagged as VERB

- **#60** yet mistagged as VERB, e.g. the best is yet to come (should be ADV)

### 4.4 Gerunds Mistagged as VERB

- **#63** Gerunds mistagged as VERB, e.g. planning in "propose planning" (should be NOUN)

---

## 5. Mistagged as Other POS

### 5.1 Nouns Mistagged as ADV

- **#12** Lunch (should be NOUN) mistagged as ADV
- **#27** casino (should be NOUN) mistagged as ADV, e.g. 唯一一個知道第一個反應係casino

### 5.2 Prepositions Mistagged as NOUN

- **#24** over (should be ADP) mistagged as NOUN, e.g. over in "voice over"

### 5.3 Other Special Mistaggings

- **#3** up mistagged as VERB; up does not function as a verb in this context
- **#7** like mistagged as ADJ; like only has NOUN and VERB as valid POS options
- **#10** wah (interjection, INTJ) mistagged as NOUN, e.g. wah 真係好靚

---

## 6. Segmentation and Recognition Issues

### 6.1 Multi-word Proper Nouns Handled Incorrectly

- **#6** Consecutive English words sometimes all tagged as NOUN
- **#20** Multi-word proper nouns split into individual tokens each tagged PROPN, e.g. Bakehouse蛋撻的撻底是酸種Sourdough Eggs Tart
- **#26** Some Hong Kong store names not recognized accurately, e.g. Vission Bakery, Bake House
- **#30** Consecutive capitalized English words should be recognized as a single PROPN unit, e.g. Now You See Me, House Keeping, Drag Queen

### 6.2 Specific Token Recognition Issues

- **#9** "po" in "po主" is an abbreviation of "post" and should be tagged as NOUN or PROPN
- **#22** feel has context-dependent POS and is frequently mistagged: when preceded by "嘅" or a verb, feel should be NOUN (e.g. 爹哋講廣東話有倪匡先生嘅feel)
- **#15** Some product names are correctly tagged as PROPN, but tagging behavior is inconsistent
- **#21** Family terms daddy, mom, uncle, mami, dad are recognized incorrectly
- **#31** "D" used as a Cantonese substitute for "的" should be tagged X and not treated as an English token
- **#32** Numbers should be tagged NUM
- **#34** part-time should be tagged as NOUN and not split into two tokens

---

## 7. Rule Suggestions

- **#19 follow rule**: If follow is preceded by a personal pronoun or person name as subject → tag as VERB
- **#22 feel rule**: If feel is preceded by "嘅" or a verb → tag feel as NOUN
- **#28 "say" verb rule**: When 說/講 precedes an English word → prioritize NOUN, e.g. 說romansh
- **#29 love rule**: If love is immediately followed by a pronoun (it / them etc.) → tag as VERB
- **#30 consecutive capitalization rule**: Multiple consecutive capitalized English words → tag as PROPN as a unit
- **#34 hyphenated compound rule**: Hyphenated words (e.g. part-time) → do not split, tag as NOUN
- **#53 contextual rule**: Preceded by adverb → following token tagged VERB; preceded by numeral → following token tagged NOUN

---

## 8. PyCantonese Improvement Note (pyt v2)

Version 2 introduced spaCy NER, improving upon v1 in the following ways:

- v1 could not extract consecutive multi-word English tokens (e.g. only "Elon" was extracted from "Elon Musk"); v2 with NER recognizes multi-word entities as a whole
- Person names and organization names such as BBC and Elon Musk are now correctly tagged as PROPN
- Limitation: the NER-first strategy sometimes over-tags common English words as PROPN
