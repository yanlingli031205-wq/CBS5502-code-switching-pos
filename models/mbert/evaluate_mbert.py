
import os
import sys
import json
import numpy as np

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)



from transformers import (
    Trainer,
    TrainingArguments,
    AutoModelForTokenClassification,
    AutoTokenizer,
    DataCollatorForTokenClassification,
)
from datasets import load_metric

# --- 1. 导入所有必要的模块 ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from models.mbert.train_with_advanced_features import load_and_prepare_datasets_with_advanced_features, tokenize_and_align_labels

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_dir = os.path.join(script_dir, "mbert-advanced-features")
    data_dir = os.path.abspath(os.path.join(script_dir, "..", "..", "data"))
    output_file = os.path.join(model_dir, "test_metrics_detailed.json")

    # --- 1. 加载模型、Tokenizer 和测试数据 ---
    print("--- Loading model, tokenizer, and data ---")
    model = AutoModelForTokenClassification.from_pretrained(model_dir)
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    
    datasets, label_list = load_and_prepare_datasets_with_advanced_features(data_dir)
    test_dataset = datasets["test"]
    tokenized_test_dataset = test_dataset.map(
        lambda p: tokenize_and_align_labels(p, tokenizer), batched=True
    )

    # --- 2. 使用 Trainer 进行评估 ---
    # 我们只需要一个临时的 Trainer 来调用 predict 方法

    data_collator = DataCollatorForTokenClassification(tokenizer)
    trainer = Trainer(model=model, data_collator=data_collator)
    print("--- Predicting on the test set ---")
    predictions, labels, _ = trainer.predict(tokenized_test_dataset)
    predictions = np.argmax(predictions, axis=2)

    # --- 3. 使用 seqeval 计算详细指标 ---
    print("--- Calculating detailed metrics ---")
    metric = load_metric("seqeval")
    
    true_predictions = [
        [label_list[p] for (p, l) in zip(prediction, label) if l != -100]
        for prediction, label in zip(predictions, labels)
    ]
    true_labels = [
        [label_list[l] for (p, l) in zip(prediction, label) if l != -100]
        for prediction, label in zip(predictions, labels)
    ]

    results = metric.compute(predictions=true_predictions, references=true_labels)

    # --- 4. 保存结果到 JSON 文件 ---
    print(f"--- Saving detailed metrics to {output_file} ---")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4, cls=NumpyEncoder)
        
    print("\n--- Overall Performance ---")
    print(f"Precision: {results['overall_precision']:.4f}")
    print(f"Recall: {results['overall_recall']:.4f}")
    print(f"F1: {results['overall_f1']:.4f}")
    print(f"Accuracy: {results['overall_accuracy']:.4f}")

if __name__ == "__main__":
    main()
