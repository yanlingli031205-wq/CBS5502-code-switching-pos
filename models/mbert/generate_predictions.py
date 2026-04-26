
import os
import sys
import numpy as np
from transformers import (
    Trainer,
    AutoModelForTokenClassification,
    AutoTokenizer,
    DataCollatorForTokenClassification,
)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from models.mbert.train_with_advanced_features import load_and_prepare_datasets_with_advanced_features, tokenize_and_align_labels

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_dir = os.path.join(script_dir, "mbert-advanced-features")
    data_dir = os.path.abspath(os.path.join(script_dir, "..", "..", "data"))
    
    # 创建 results 文件夹
    results_dir = os.path.join(script_dir, "results")
    os.makedirs(results_dir, exist_ok=True)
    output_file = os.path.join(results_dir, "test_pred.conll")

    # --- 1. 加载模型、Tokenizer 和测试数据 ---
    print("--- Loading model, tokenizer, and data ---")
    model = AutoModelForTokenClassification.from_pretrained(model_dir)
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    label_list = [model.config.id2label[i] for i in range(model.config.num_labels)]
    
    datasets, _ = load_and_prepare_datasets_with_advanced_features(data_dir)
    test_dataset = datasets["test"]
    tokenized_test_dataset = test_dataset.map(
        lambda p: tokenize_and_align_labels(p, tokenizer), 
        batched=True,
        remove_columns=test_dataset.column_names
    )

    # --- 2. 使用 Trainer 进行预测 ---
    data_collator = DataCollatorForTokenClassification(tokenizer)
    trainer = Trainer(model=model, data_collator=data_collator)
    print("--- Predicting on the test set ---")
    predictions, labels, _ = trainer.predict(tokenized_test_dataset)
    predictions = np.argmax(predictions, axis=2)

    # --- 3. 将预测ID转换回标签 ---
    true_predictions = [
        [label_list[p] for (p, l) in zip(prediction, label) if l != -100]
        for prediction, label in zip(predictions, labels)
    ]

    # --- 4. 将结果写入 CoNLL 文件 ---
    print(f"--- Writing predictions to {output_file} ---")
    with open(output_file, "w", encoding="utf-8") as writer:
        for i, sentence_preds in enumerate(true_predictions):
            original_tokens = test_dataset[i]["tokens"]
            for token, pred in zip(original_tokens, sentence_preds):
                writer.write(f"{token} {pred}\n")
            writer.write("\n") # 句子间空一行

    print("Prediction file generated successfully.")

if __name__ == "__main__":
    main()
