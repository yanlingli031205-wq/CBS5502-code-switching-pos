
import datasets
from datasets import load_dataset, load_metric, Dataset, DatasetDict
from transformers import AutoTokenizer, AutoModelForTokenClassification, TrainingArguments, Trainer
import torch
import numpy as np
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from utils.io import read_conll

# 1. 加载数据集
def load_and_prepare_datasets(data_dir):

    train_sents = read_conll(os.path.join(data_dir, "train.conll"))
    val_sents = read_conll(os.path.join(data_dir, "dev.conll"))
    test_sents = read_conll(os.path.join(data_dir, "test.conll"))

    # 从句子创建Hugging Face数据集
    train_dataset = Dataset.from_dict({
        key: [d[key] for d in train_sents] for key in train_sents[0]
    })
    val_dataset = Dataset.from_dict({
        key: [d[key] for d in val_sents] for key in val_sents[0]
    })
    test_dataset = Dataset.from_dict({
        key: [d[key] for d in test_sents] for key in test_sents[0]
    })

    # 获取所有唯一的标签
    unique_tags = set(tag for sent in train_sents for tag in sent["pos_tags"])
    unique_tags.update(set(tag for sent in val_sents for tag in sent["pos_tags"]))
    unique_tags.update(set(tag for sent in test_sents for tag in sent["pos_tags"]))
    tag_list = sorted(list(unique_tags))

    # 为pos_tags列应用ClassLabel
    train_dataset = train_dataset.cast_column("pos_tags", datasets.Sequence(feature=datasets.ClassLabel(names=tag_list)))
    val_dataset = val_dataset.cast_column("pos_tags", datasets.Sequence(feature=datasets.ClassLabel(names=tag_list)))
    test_dataset = test_dataset.cast_column("pos_tags", datasets.Sequence(feature=datasets.ClassLabel(names=tag_list)))

    return DatasetDict({"train": train_dataset, "validation": val_dataset, "test": test_dataset})

# 2. 定义模型和分词器
model_checkpoint = "bert-base-multilingual-cased"
tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)

# 3. 预处理数据
def tokenize_and_align_labels(examples, tokenizer, label_all_tokens=True):
    tokenized_inputs = tokenizer(
        examples["tokens"], truncation=True, is_split_into_words=True
    )

    labels = []
    for i, label in enumerate(examples["pos_tags"]):
        word_ids = tokenized_inputs.word_ids(batch_index=i)
        previous_word_idx = None
        label_ids = []
        for word_idx in word_ids:
            if word_idx is None:
                label_ids.append(-100)
            elif word_idx != previous_word_idx:
                label_ids.append(label[word_idx])
            else:
                label_ids.append(-100)
            previous_word_idx = word_idx

        labels.append(label_ids)

    tokenized_inputs["labels"] = labels
    return tokenized_inputs

# 4. 评估指标
metric = load_metric("seqeval")

def compute_metrics(p, label_list):
    predictions, labels = p
    predictions = np.argmax(predictions, axis=2)

    true_predictions = [
        [label_list[p] for (p, l) in zip(prediction, label) if l != -100]
        for prediction, label in zip(predictions, labels)
    ]
    true_labels = [
        [label_list[l] for (p, l) in zip(prediction, label) if l != -100]
        for prediction, label in zip(predictions, labels)
    ]

    results = metric.compute(predictions=true_predictions, references=true_labels)
    return {
        "precision": results["overall_precision"],
        "recall": results["overall_recall"],
        "f1": results["overall_f1"],
        "accuracy": results["overall_accuracy"],
    }


if __name__ == "__main__":
    # 获取数据目录的绝对路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.abspath(os.path.join(script_dir, "..", "..", "data"))

    # 加载数据集
    datasets = load_and_prepare_datasets(data_dir)
    
    # 从训练数据集中获取标签列表
    label_list = datasets["train"].features["pos_tags"].feature.names

    # 对数据集进行tokenize和标签对齐
    tokenized_datasets = datasets.map(tokenize_and_align_labels, batched=True, fn_kwargs={"tokenizer": tokenizer})

    # 加载模型
    model = AutoModelForTokenClassification.from_pretrained(
        model_checkpoint, num_labels=len(label_list)
    )
    # 【核心修正】将标签映射写入模型配置，以便正确保存和加载
    model.config.id2label = {i: label for i, label in enumerate(label_list)}
    model.config.label2id = {label: i for i, label in enumerate(label_list)}

    # 定义训练参数
    output_dir = os.path.join(script_dir, "test-ner-output") # 恢复到最佳模型的输出目录
    args = TrainingArguments(
        output_dir=output_dir,
        evaluation_strategy="epoch",
        save_strategy="no", # 禁止在训练中途自动保存
        learning_rate=2e-5, # 恢复到已知的最佳学习率
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        num_train_epochs=10, # 使用完整的训练周期
        weight_decay=0.01,
        warmup_ratio=0.1, # 新增：10%的训练步数用于预热
        lr_scheduler_type="cosine", # 新增：使用余弦衰减策略
    )

    # 数据整理器
    from transformers import DataCollatorForTokenClassification
    data_collator = DataCollatorForTokenClassification(tokenizer)

    # 定义训练器
    trainer = Trainer(
        model,
        args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["validation"],
        data_collator=data_collator,
        tokenizer=tokenizer,
        compute_metrics=lambda p: compute_metrics(p, label_list=label_list),
    )

    # 开始训练
    trainer.train()

    # 在测试集上评估
    eval_results = trainer.evaluate(tokenized_datasets["test"])
    print("Evaluation results on the test set:")
    print(eval_results)

    # 保存模型
    # 手动仅保存模型权重和配置，以减小体积
    model.save_pretrained(output_dir)
    print(f"Model saved to {output_dir}")
