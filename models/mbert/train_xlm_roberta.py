
import os
import shutil
import sys
from transformers import (
    Trainer,
    TrainingArguments,
    AutoModelForTokenClassification,
    AutoTokenizer,
    DataCollatorForTokenClassification,
)

# 将项目根目录添加到sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from models.mbert.train import (
    load_and_prepare_datasets,
    tokenize_and_align_labels,
    compute_metrics,
)

def main():
    # --- 1. 设置模型和目录 ---
    model_checkpoint = "xlm-roberta-base"  # 关键改动：使用XLM-R
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "xlm-roberta-model")

    print(f"--- Starting Experiment with {model_checkpoint} ---")
    print(f"Output will be saved to: {output_dir}")

    # --- 2. 加载和预处理数据 ---
    data_dir = os.path.abspath(os.path.join(script_dir, "..", "..", "data"))
    datasets = load_and_prepare_datasets(data_dir)
    label_list = datasets["train"].features["pos_tags"].feature.names

    tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
    # 注意：XLM-R的分词器可能与mBERT不同，但我们的函数是通用的，可以处理
    tokenized_datasets = datasets.map(
        lambda p: tokenize_and_align_labels(p, tokenizer), batched=True
    )

    # --- 3. 加载模型并设置标签映射 ---
    model = AutoModelForTokenClassification.from_pretrained(
        model_checkpoint, num_labels=len(label_list)
    )
    model.config.id2label = {i: label for i, label in enumerate(label_list)}
    model.config.label2id = {label: i for i, label in enumerate(label_list)}

    # --- 4. 定义训练参数 (保留每一代) ---
    args = TrainingArguments(
        output_dir=output_dir,
        evaluation_strategy="epoch",
        save_strategy="no",  # 关键改动：禁止中途保存以避免空间问题
        learning_rate=2e-5,  # 使用我们之前发现效果不错的学习率作为起点
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        num_train_epochs=10,
        weight_decay=0.01,
    )

    # --- 5. 初始化训练器并开始训练 ---
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

    print("--- Starting Training ---")
    trainer.train()
    print("--- Training Finished ---")

    # --- 6. 评估并保存最终的最佳模型 ---
    print("--- Evaluating on Test Set with the Best Model ---")
    eval_results = trainer.evaluate(eval_dataset=tokenized_datasets["test"])
    print("Final evaluation results on the test set:")
    print(eval_results)

    # Trainer在load_best_model_at_end=True时已加载最佳模型，我们只需保存即可
    print("--- Saving the Best Model ---")
    trainer.save_model(output_dir) # 保存最终的最佳模型
    print(f"Best model saved to {output_dir}")

if __name__ == "__main__":
    main()
