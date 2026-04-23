
import os
import sys
from transformers import (
    Trainer,
    TrainingArguments,
    AutoModelForTokenClassification,
    AutoTokenizer,
    DataCollatorForTokenClassification,
)

# 【核心改动】将项目根目录添加到sys.path，并导入我们需要的函数和词汇表
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from models.mbert.train import (
    load_and_prepare_datasets as original_load_and_prepare_datasets,
    tokenize_and_align_labels,
    compute_metrics,
)
from models.rule_based.rule_based_tagger import (
    INTJ_LEXICON, X_LEXICON, PROPN_LEXICON, VERB_LEXICON, ADJ_LEXICON, ADV_LEXICON, NOUN_LEXICON
)

# --- 1. 定义词汇表和特征 --- 
LEXICONS = {
    "INTJ": INTJ_LEXICON,
    "X": X_LEXICON,
    "PROPN": PROPN_LEXICON,
    "VERB": VERB_LEXICON,
    "ADJ": ADJ_LEXICON,
    "ADV": ADV_LEXICON,
    "NOUN": NOUN_LEXICON,
}

def get_feature_tags(token):
    """根据词元所属的词汇表，为其生成特征标签。"""
    tags = []
    token_lower = token.lower()
    for name, lexicon in LEXICONS.items():
        if token_lower in lexicon:
            tags.append(f"[FEAT_{name}]")
    return " ".join(tags)

def preprocess_with_features(example):
    """将特征标签拼接到原始词元上。"""
    new_tokens = []
    for token in example["tokens"]:
        feature_tags = get_feature_tags(token)
        if feature_tags:
            new_tokens.append(f"{token} {feature_tags}")
        else:
            new_tokens.append(token)
    example["tokens"] = new_tokens
    return example

# --- 2. 包装新的数据加载函数 ---
def load_and_prepare_datasets_with_features(data_dir):
    datasets = original_load_and_prepare_datasets(data_dir)
    
    print("--- Injecting Lexicon Features into Datasets ---")
    featured_datasets = datasets.map(preprocess_with_features)
    
    # 打印一个例子以供检查
    print("\n--- Example with Injected Features ---")
    print(featured_datasets["train"][0]["tokens"])
    print("------------------------------------\n")
    
    return featured_datasets


def main():
    # --- 3. 设置模型和目录 ---
    model_checkpoint = "bert-base-multilingual-cased"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "mbert-with-features")

    # --- 4. 加载和预处理数据 ---
    data_dir = os.path.abspath(os.path.join(script_dir, "..", "..", "data"))
    datasets = load_and_prepare_datasets_with_features(data_dir)
    label_list = datasets["train"].features["pos_tags"].feature.names

    tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
    tokenized_datasets = datasets.map(
        lambda p: tokenize_and_align_labels(p, tokenizer), batched=True
    )

    # --- 5. 加载模型并训练 ---
    model = AutoModelForTokenClassification.from_pretrained(
        model_checkpoint, num_labels=len(label_list)
    )
    model.config.id2label = {i: label for i, label in enumerate(label_list)}
    model.config.label2id = {label: i for i, label in enumerate(label_list)}

    args = TrainingArguments(
        output_dir=output_dir,
        evaluation_strategy="epoch",
        save_strategy="no",
        learning_rate=2e-5, 
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        num_train_epochs=10,
        weight_decay=0.01,
    )

    data_collator = DataCollatorForTokenClassification(tokenizer)
    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["validation"],
        data_collator=data_collator,
        tokenizer=tokenizer,
        compute_metrics=lambda p: compute_metrics(p, label_list=label_list),
    )

    trainer.train()

    # --- 6. 评估和保存 ---
    print("--- Evaluating on Test Set ---")
    eval_results = trainer.evaluate(eval_dataset=tokenized_datasets["test"])
    print(eval_results)

    print("--- Saving Final Model ---")
    model.save_pretrained(output_dir)
    print(f"Model with features saved to {output_dir}")

if __name__ == "__main__":
    main()
