# CBS5502 Group Project — Code-Switching POS Tagging

## 项目概览

粤英混码（Code-Switching）词性标注研究。比较 Baseline / Rule-based / BiLSTM-CRF / mBERT 四种方法在粤英混码句子上的表现。

## 成员分工

| 成员 | 负责步骤 | 状态 |
|------|----------|------|
| zqy | Step 1 数据收集 | 完成 |
| pyt | Step 2 PyCantonese 自动标注 | 完成 |
| **lyl** | **Step 3 人工修正 Gold Standard + Step 4a Rule-based** | **Step 3 完成 / Step 4a 进行中** |
| zxy | Step 4b BiLSTM-CRF | 可开始（请使用 data/train.conll + data/dev.conll + data/test.conll） |
| szq | Step 4c mBERT fine-tune | 可开始（请使用 data/train.conll + data/dev.conll + data/test.conll） |
| pyt | Step 5 评估 & 结果分析 | 待所有模型完成 |

---

## 文件夹结构

```
CBS5502_group_project_code_switching/
│
├── corpus/                        ← 原始数据（zqy + pyt 完成）
│   ├── CBS5502group.xlsx          ← zqy 收集的 300 条原始语料
│   ├── token_langid_all.csv       ← pyt：全部 token 的自动标注结果
│   └── english_tokens.csv         ← pyt 给 lyl 的待填表格（只含英文 token）
│
├── annotation/                    ← lyl 的工作输出
│   ├── gold_standard/             ← gold standard 文件（lyl 完成）
│   │   ├── gold_standard_completed.csv   ← 完整人工标注结果（含 / 行）
│   │   ├── gold_standard_cleaned.csv     ← ⭐ 清洗后版本（供模型训练与评估使用）
│   │   └── annotation_report.md          ← 标注统计报告（正确率 48.86%）
│   └── error_analysis/            ← 错误分析
│       └── error_analysis_report.md      ← 71 条错误归类（中英双语）
│
├── models/
│   ├── rule_based/                ← lyl 的 rule-based 系统
│   │   ├── rules.py
│   │   └── run_rules.py
│   ├── bilstm_crf/                ← zxy 的工作
│   └── mbert/                     ← szq 的工作
│
├── evaluation/                    ← pyt 的评估脚本和结果
│
├── report/
│   └── figures/                   ← 图表截图
│
├── data/                          ← ⭐ Step 4 模型输入（CoNLL 格式，70/15/15 划分）
│   ├── train.conll                ← 训练集（216 句，388 tokens）
│   ├── dev.conll                  ← 验证集（46 句，76 tokens）
│   └── test.conll                 ← 测试集（47 句，98 tokens）
│
├── scripts/                       ← 公用脚本
│   └── split_to_conll.py          ← 生成上述 CoNLL 文件的脚本（seed=42）
│
├── README.md
├── full_project_pipeline.svg
└── team_pipeline_with_names.html
```

---

## lyl 的具体任务

### Step 3：人工修正 → Gold Standard ✅ 已完成

**输入文件**：`corpus/english_tokens.csv`

该文件每行一个句子，格式为：
```
original_text | en_token_1 | auto_pos_1 | gold_pos_1 | en_token_2 | auto_pos_2 | gold_pos_2 | ...
```

**你只需要填写 `gold_pos_*` 列**：
- 检查每个英文 token 的 `auto_pos`（PyCantonese 自动标注的词性）
- 如果正确 → `gold_pos` 填与 `auto_pos` 相同的词性
- 如果错误 → `gold_pos` 填正确的词性

**词性标签参考（Universal POS Tags）**：

| 标签 | 含义 | 例子 |
|------|------|------|
| NOUN | 普通名词 | app, post, banner |
| PROPN | 专有名词 | Tesla, Trump, iPhone |
| VERB | 动词 | claim, bookmark, summarize |
| ADJ | 形容词 | cool, good, hot |
| ADV | 副词 | really, very, just |
| NUM | 数词 | one, two, 100 |
| PRON | 代词 | I, you, it |
| DET | 限定词 | the, a, this |
| ADP | 介词 | in, on, at |
| CONJ | 连词 | and, but, or |
| INTJ | 感叹词 | wow, oh, lol |
| X | 无法分类 | 缩写、网络词 |

**完成后**：
- `annotation/gold_standard/gold_standard_completed.csv`：完整标注结果
- `annotation/gold_standard/gold_standard_cleaned.csv`：清洗后版本（移除 PyCantonese 未识别的 27 个 token 所在的 25 句）
- **后续步骤请使用 `gold_standard_cleaned.csv`**

**标注结果统计**：
- 总句子：335 句，英文 token：569 个（cleaned）
- PyCantonese 自动标注正确率：**48.86%**
- 详见 `annotation/gold_standard/annotation_report.md`

### Step 3 同时：错误分析 ✅ 已完成

归纳 71 条 PyCantonese 标注错误，分为 PROPN 过度标注、NOUN 过度标注、误判为 ADJ/VERB/其他词性、分词识别问题、规则建议共 7 大类，含中英双语版本。

详见 `annotation/error_analysis/error_analysis_report.md`

### Step 4（公共数据）：CoNLL 划分 ✅ 已完成

由 `scripts/split_to_conll.py` 生成，输出到 `data/` 目录。

**格式**（CoNLL，token + TAB + gold_pos，句间空行）：
```
# sent_id = 3
# text = 搵林律師claim爆你每架連機師補品賠10億美金！
claim	VERB

# sent_id = 4
...
```

**划分统计**（总计 309 条有效句子，1 条因 gold_pos 全空被过滤）：

| 集合 | 句子数 | Token 数 | 用途 |
|------|--------|----------|------|
| train.conll | 216 | 388 | 模型训练 |
| dev.conll   | 46  | 76  | 超参调优 |
| test.conll  | 47  | 98  | 最终评估（所有模型使用同一测试集） |

- 随机种子：`random.seed(42)`，结果可复现
- Rule-based 只需读取 `test.conll` 进行评估，无需 train/dev

### Step 4a：Rule-based 修正

根据错误分析结果，设计消歧规则，在 `models/rule_based/` 下用 Python 实现。

---

## 数据处理备注

### pyt 标注表格的版本迭代

**问题（v1）**：pyt 第一版交给 lyl 的表格（`english_tokens.csv`）存在英文 token 漏提取的问题——当句子中出现连续多个英文词时（如 `Donald Trump`、`Elon Musk`、`final fantasy`），PyCantonese 仅对第一个英文词做了 POS 标注，后续紧跟的英文词未被提取。

**原因**：PyCantonese 的分词器在处理粤英混码时，对连续 ASCII 序列的切分逻辑不稳定，部分情况下会将多词序列视为单一单元，或仅保留首词的标注结果。

**修复（v2）**：pyt 修改了数据清洗流程，引入 NER（命名实体识别）库，并设置 NER 结果强制优先，使命名实体（如人名、地名、品牌名等多词结构）能被完整切分和提取，不再出现漏词。修复后的文件即现版本 `corpus/english_tokens_copy.csv`。

**对 lyl 工作的影响**：lyl 在 v1 表格中已自行补填了部分缺失 token（在对应列手动添加 token，`auto_pos` 填 `?`，`gold_pos` 填正确词性并黄色高亮标注）。v2 版本解决了该问题，后续不再需要手动补填。

---

## GitHub 项目建立流程

仓库地址：[https://github.com/yanlingli031205-wq/CBS5502-code-switching-pos](https://github.com/yanlingli031205-wq/CBS5502-code-switching-pos)

### 组员如何克隆项目

```bash
git clone https://github.com/yanlingli031205-wq/CBS5502-code-switching-pos.git
```

### 组员如何提交自己的文件

```bash
# 1. 把文件放到对应文件夹
# 2. 在终端运行：
git add .
git commit -m "描述你做了什么，例如：add gold standard annotation"
git push
```

### 邀请组员协作

仓库页面 → Settings → Collaborators → Add people → 填入对方 GitHub 用户名
