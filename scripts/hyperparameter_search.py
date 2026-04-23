
import os
import sys
import shutil

# 【核心修正】将项目根目录添加到Python的模块搜索路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from transformers import Trainer, TrainingArguments, AutoModelForTokenClassification, AutoTokenizer
from models.mbert.train import load_and_prepare_datasets, tokenize_and_align_labels, compute_metrics

def main():
    # --- 1. 定义搜索空间和基础设置 ---
    learning_rates_to_try = [1e-5, 2e-5, 3e-5, 5e-5]
    best_f1 = -1.0
    best_learning_rate = None
    results = {}

    # --- 2. 加载和预处理数据 (一次性完成) ---
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.abspath(os.path.join(script_dir, "..", "data"))
    datasets = load_and_prepare_datasets(data_dir)
    label_list = datasets["train"].features["pos_tags"].feature.names
    
    model_checkpoint = "bert-base-multilingual-cased"
    tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
    tokenized_datasets = datasets.map(lambda p: tokenize_and_align_labels(p, tokenizer), batched=True)

    # --- 3. 循环遍历超参数进行训练和评估 ---
    for lr in learning_rates_to_try:
        print(f"\n{'='*20} Training with Learning Rate: {lr} {'='*20}")

        # 每次循环都重新加载模型，避免权重泄露
        model = AutoModelForTokenClassification.from_pretrained(model_checkpoint, num_labels=len(label_list))
        model.config.id2label = {i: label for i, label in enumerate(label_list)}
        model.config.label2id = {label: i for i, label in enumerate(label_list)}

        # 定义训练参数
        output_dir = os.path.join(script_dir, f"hp-search-lr-{lr}")
        args = TrainingArguments(
            output_dir=output_dir,
            evaluation_strategy="epoch",
            learning_rate=lr,
            per_device_train_batch_size=16,
            per_device_eval_batch_size=16,
            num_train_epochs=5,  # 减少epoch以加快搜索速度
            weight_decay=0.01,
            load_best_model_at_end=False, # 禁用，因为我们不保存
            save_strategy="no",
        )

        # 定义数据整理器
        from transformers import DataCollatorForTokenClassification
        data_collator = DataCollatorForTokenClassification(tokenizer)

        # 定义训练器
        trainer = Trainer(
            model=model,
            args=args,
            train_dataset=tokenized_datasets["train"],
            eval_dataset=tokenized_datasets["validation"],
            data_collator=data_collator,
            tokenizer=tokenizer,
            compute_metrics=lambda p: compute_metrics(p, label_list=label_list),
        )

        # 开始训练
        trainer.train()

        # 在验证集上评估，找到当前学习率下的最佳F1
        eval_results = trainer.evaluate()
        current_f1 = eval_results["eval_f1"]
        results[lr] = current_f1
        print(f"F1 score for learning rate {lr}: {current_f1}")

        if current_f1 > best_f1:
            best_f1 = current_f1
            best_learning_rate = lr
        
        # 清理掉这次运行的输出，节省空间
        try:
            shutil.rmtree(output_dir)
            print(f"Cleaned up directory: {output_dir}")
        except OSError as e:
            print(f"Error cleaning up directory {output_dir}: {e.strerror}")

    # --- 4. 打印最终结果 ---
    print(f"\n{'='*20} Hyperparameter Search Complete {'='*20}")
    print(f"Best F1 score on validation set: {best_f1}")
    print(f"Best learning rate: {best_learning_rate}")
    print("\n--- All Results ---")
    for lr, f1 in results.items():
        print(f"LR: {lr} -> F1: {f1}")

if __name__ == "__main__":
    main()
