# CBS5502 Group Project — Code-Switching POS Tagging

## 项目概览

粤英混码（Code-Switching）词性标注研究。比较 Baseline / Rule-based / BiLSTM-CRF / mBERT 四种方法在粤英混码句子上的表现。

## 成员分工

| 成员 | 负责步骤 | 状态 |
|------|----------|------|
| zqy | Step 1 数据收集 | 完成 |
| pyt | Step 2 PyCantonese 自动标注 | 完成 |
| **lyl** | **Step 3 人工修正 Gold Standard + Step 4a Rule-based** | **进行中** |
| zxy | Step 4b BiLSTM-CRF | 待 Gold Standard |
| szq | Step 4c mBERT fine-tune | 待 Gold Standard |
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
│   ├── gold_standard/             ← 放完成后的 gold standard 文件
│   │   └── gold_standard.csv      ← (lyl 产出，供全组共用)
│   └── error_analysis/            ← 放错误分析统计
│       └── error_analysis.csv     ← (lyl 产出，供 report 使用)
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
├── scripts/                       ← 公用脚本
│
├── README.md
├── full_project_pipeline.svg
└── team_pipeline_with_names.html
```

---

## lyl 的具体任务

### Step 3：人工修正 → Gold Standard

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

**完成后**：把填完的文件另存为 `annotation/gold_standard/gold_standard.csv`

### Step 3 同时：错误分析

统计 auto_pos ≠ gold_pos 的案例，记录错误类型（如：NOUN 被标成 VERB），存入 `annotation/error_analysis/error_analysis.csv`

格式建议：
```
token | context | auto_pos | gold_pos | error_type | note
```

### Step 4a：Rule-based 修正

根据错误分析结果，设计消歧规则，在 `models/rule_based/` 下用 Python 实现。

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
