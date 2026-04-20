"""
split_to_conll.py
-----------------
将 gold_standard_cleaned.csv（wide format）转换为 CoNLL 格式，
并按 70 / 15 / 15 划分为 train / dev / test。

输出目录：data/
  data/train.conll
  data/dev.conll
  data/test.conll

CoNLL 格式示例：
  # sent_id = 3
  # text = 搵林律師claim爆你每架連機師補品賠10億美金！
  claim	VERB

  # sent_id = 4
  ...
"""

import csv
import random
from pathlib import Path

# ── 路径配置 ────────────────────────────────────────────────────────────────
BASE = Path(__file__).parent.parent
SRC  = BASE / "annotation" / "gold_standard_use_cleaned_version" / "gold_standard_cleaned.csv"
OUT  = BASE / "data"
OUT.mkdir(exist_ok=True)

# ── 读取数据 ────────────────────────────────────────────────────────────────
sentences = []   # list of {"sent_id": int, "text": str, "tokens": [(token, gold_pos), ...]}

with open(SRC, encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)   # 跳过表头

    for row_num, row in enumerate(reader, start=1):
        if not row or not row[0].strip():
            continue

        text = row[0].strip()
        tokens = []

        # 每组 3 列：en_token_N, auto_pos_N, gold_pos_N
        num_slots = (len(row) - 1) // 3
        for i in range(num_slots):
            base = 1 + i * 3
            en_token = row[base].strip()   if base     < len(row) else ""
            gold_pos  = row[base + 2].strip() if base + 2 < len(row) else ""

            if en_token and gold_pos:          # 只保留有 gold 标注的 token
                tokens.append((en_token, gold_pos))

        if tokens:                             # 至少有一个 token 才保留句子
            sentences.append({
                "sent_id": row_num,
                "text":    text,
                "tokens":  tokens,
            })

print(f"有效句子数（含 ≥1 个已标注 token）：{len(sentences)}")

# ── 随机划分（固定 seed 保证可复现）────────────────────────────────────────
random.seed(42)
indices = list(range(len(sentences)))
random.shuffle(indices)

n = len(sentences)
n_train = int(n * 0.70)
n_dev   = int(n * 0.15)
# test 取剩余全部，避免因取整丢数据
n_test  = n - n_train - n_dev

train_idx = indices[:n_train]
dev_idx   = indices[n_train : n_train + n_dev]
test_idx  = indices[n_train + n_dev :]

splits = {
    "train": [sentences[i] for i in train_idx],
    "dev":   [sentences[i] for i in dev_idx],
    "test":  [sentences[i] for i in test_idx],
}

print(f"train: {len(splits['train'])}  dev: {len(splits['dev'])}  test: {len(splits['test'])}")

# ── 写出 CoNLL 文件 ─────────────────────────────────────────────────────────
def write_conll(path: Path, sents: list):
    with open(path, "w", encoding="utf-8") as f:
        for s in sents:
            f.write(f"# sent_id = {s['sent_id']}\n")
            f.write(f"# text = {s['text']}\n")
            for token, gold_pos in s["tokens"]:
                f.write(f"{token}\t{gold_pos}\n")
            f.write("\n")   # 句子之间空行

for split_name, sents in splits.items():
    out_path = OUT / f"{split_name}.conll"
    write_conll(out_path, sents)
    print(f"已写出 {out_path}  ({len(sents)} 句)")

print("\n完成！文件位于 data/ 目录。")
