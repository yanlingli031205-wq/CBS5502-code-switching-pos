
import os
import sys
from transformers import (
    Trainer,
    TrainingArguments,
    AutoModelForTokenClassification,
    AutoTokenizer,
    DataCollatorForTokenClassification,
)

# --- 1. 导入所有必要的模块和 lyl 的专家知识 ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from models.mbert.train import (
    load_and_prepare_datasets, # 使用原始的加载函数
    tokenize_and_align_labels,
    compute_metrics,
)
from models.rule_based.rule_based_tagger import (
    INTJ_LEXICON, X_LEXICON, PROPN_LEXICON, VERB_LEXICON, ADJ_LEXICON, ADV_LEXICON, NOUN_LEXICON,
    NEEDS_CONTEXT, _context_pos # 导入语境规则所需的核心函数和词表
)

# --- 2. 定义特征提取逻辑 ---
LEXICONS = {
    "INTJ": INTJ_LEXICON, "X": X_LEXICON, "PROPN": PROPN_LEXICON, 
    "VERB": VERB_LEXICON, "ADJ": ADJ_LEXICON, "ADV": ADV_LEXICON, "NOUN": NOUN_LEXICON
}

def get_advanced_features(token, sentence_text):
    """为词元生成包含词汇表和语境规则的特征标签。"""
    tags = []
    token_lower = token.lower()

    # a. 添加词汇表特征
    for name, lexicon in LEXICONS.items():
        if token_lower in lexicon:
            tags.append(f"[FEAT_{name}]")
            
    # b. 【核心改动】添加语境规则特征
    if token_lower in NEEDS_CONTEXT and sentence_text:
        context_prediction = _context_pos(token, sentence_text)
        if context_prediction:
            tags.append(f"[CTX_{context_prediction}]") # e.g., [CTX_NOUN]
            
    return " ".join(tags)

def preprocess_with_advanced_features(example):
    """将高级特征拼接到原始词元上。"""
    new_tokens_for_sentence = []
    # 我们需要同时访问 tokens 和完整的句子 text
    for i, token in enumerate(example["tokens"]):
        # 从原始数据中获取对应的完整句子文本
        # 注意：这里假设 example 是单个样本，而不是批处理
        sentence_text = example["text"]
        feature_tags = get_advanced_features(token, sentence_text)
        if feature_tags:
            new_tokens_for_sentence.append(f"{token} {feature_tags}")
        else:
            new_tokens_for_sentence.append(token)
    example["tokens"] = new_tokens_for_sentence
    return example

# --- 3. 包装新的数据加载函数 ---
def load_and_prepare_datasets_with_advanced_features(data_dir):
    # 这里我们需要一个能同时加载 token 和 text 的加载器
    # 我们将直接使用 rule_based_tagger.py 中的 read_conll 函数
    from models.rule_based.rule_based_tagger import read_conll as read_conll_fully
    from datasets import Dataset, DatasetDict

    train_sents = read_conll_fully(os.path.join(data_dir, "train.conll"))
    val_sents = read_conll_fully(os.path.join(data_dir, "dev.conll"))
    test_sents = read_conll_fully(os.path.join(data_dir, "test.conll"))

    # 将数据转换为 Hugging Face Dataset 对象
    def create_dataset(sents):
        return Dataset.from_dict({
            "id": [s["sent_id"] for s in sents],
            "text": [s["text"] for s in sents],
            "tokens": [ [t[0] for t in s["tokens"]] for s in sents],
            "pos_tags": [ [t[1] for t in s["tokens"]] for s in sents],
        })

    datasets = DatasetDict({
        "train": create_dataset(train_sents),
        "validation": create_dataset(val_sents),
        "test": create_dataset(test_sents)
    })

    print("--- Injecting Advanced (Lexicon + Context) Features ---")
    featured_datasets = datasets.map(preprocess_with_advanced_features, load_from_cache_file=False)
    
    # 打印一个例子以供检查
    print("\n--- Example with Injected Advanced Features ---")
    # 寻找一个包含歧义词 'like' 的例子
    for sample in featured_datasets["train"]:
        if any("like" in t.lower() for t in sample["tokens"]):
            print(sample["tokens"])
            break
    print("-------------------------------------------\n")
    
    # 转换 pos_tags 为 ClassLabel
    label_list = sorted(list(set(tag for split in featured_datasets.values() for sent in split["pos_tags"] for tag in sent)))
    for split in featured_datasets.keys():
        featured_datasets[split] = featured_datasets[split].cast_column("pos_tags", 
            sys.modules["datasets"].Sequence(feature=sys.modules["datasets"].ClassLabel(names=label_list))
        )

    return featured_datasets, label_list

def main():
    # ... 主函数逻辑与之前类似, 但使用新的数据加载 ...
    model_checkpoint = "bert-base-multilingual-cased"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "mbert-advanced-features")

    datasets, label_list = load_and_prepare_datasets_with_advanced_features(os.path.abspath(os.path.join(script_dir, "..", "..", "data")))

    tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
    tokenized_datasets = datasets.map(
        lambda p: tokenize_and_align_labels(p, tokenizer), batched=True
    )

    model = AutoModelForTokenClassification.from_pretrained(
        model_checkpoint, num_labels=len(label_list)
    )
    model.config.id2label = {i: label for i, label in enumerate(label_list)}
    model.config.label2id = {label: i for i, label in enumerate(label_list)}

    args = TrainingArguments(
        output_dir=output_dir,
        evaluation_strategy="epoch",
        save_strategy="epoch", # 按您的要求，保存每一代
        learning_rate=2e-5, 
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        num_train_epochs=10,
        weight_decay=0.01,
        load_best_model_at_end=True,
        metric_for_best_model="f1",
    )

    data_collator = DataCollatorForTokenClassification(tokenizer)
    trainer = Trainer(
        model=model, args=args, train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["validation"], data_collator=data_collator,
        tokenizer=tokenizer, compute_metrics=lambda p: compute_metrics(p, label_list=label_list)
    )

    trainer.train()

    print("--- Evaluating on Test Set with the Best Model ---")
    eval_results = trainer.evaluate(eval_dataset=tokenized_datasets["test"])
    print(eval_results)

    print("--- Saving the Best Model ---")
    trainer.save_model(output_dir)
    print(f"Model with advanced features saved to {output_dir}")

if __name__ == "__main__":
    main()
