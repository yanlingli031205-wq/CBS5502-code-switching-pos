
import os
import torch
import sys
from transformers import AutoTokenizer, AutoModelForTokenClassification

# --- 1. 导入所有必要的模块和 lyl 的专家知识 ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.mbert.train_with_advanced_features import (
    get_advanced_features, 
    preprocess_with_advanced_features as original_preprocess
)
from models.rule_based.rule_based_tagger import read_conll as read_conll_fully

def main():
    # --- 2. 设置路径 ---
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_dir = os.path.join(script_dir, "..", "models", "mbert", "mbert-advanced-features")
    data_file = os.path.join(script_dir, "..", "data", "test.conll")

    # --- 3. 加载模型和分词器 ---
    if not os.path.exists(model_dir) or not os.path.exists(os.path.join(model_dir, "pytorch_model.bin")):
        print(f"Model not found in {model_dir}.")
        return

    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    model = AutoModelForTokenClassification.from_pretrained(model_dir)
    print("Model and tokenizer loaded successfully.")

    # --- 4. 加载并预处理数据 ---
    id2label = model.config.id2label
    test_sents_raw = read_conll_fully(data_file)
    if not test_sents_raw:
        print(f"No valid data found in {data_file}")
        return

    # 创建一个可以被 map 的 Dataset 对象
    from datasets import Dataset
    test_dataset = Dataset.from_dict({
        "id": [s["sent_id"] for s in test_sents_raw],
        "text": [s["text"] for s in test_sents_raw],
        "tokens": [ [t[0] for t in s["tokens"]] for s in test_sents_raw],
        "pos_tags": [ [t[1] for t in s["tokens"]] for s in test_sents_raw],
    })

    # 【核心改动】注入与训练时完全相同的特征
    print("--- Injecting Advanced Features for Prediction ---")
    featured_test_dataset = test_dataset.map(original_preprocess)

    # --- 5. 逐句预测和错误分析 ---
    print("\n--- Prediction Error Analysis ---")
    total_errors = 0
    total_tokens = 0
    correct_predictions = 0

    for i, sent in enumerate(featured_test_dataset):
        # 注意：sent["tokens"] 此刻是带有特征的
        tokens_with_features = sent["tokens"]
        # 我们需要原始的 token 用于最终的展示
        original_tokens = test_dataset[i]["tokens"]
        true_tags = sent["pos_tags"]
        total_tokens += len(original_tokens)

        # 使用带有特征的 token 进行分词和预测
        tokenized_inputs = tokenizer(tokens_with_features, truncation=True, is_split_into_words=True, return_tensors="pt")
        
        with torch.no_grad():
            logits = model(**tokenized_inputs).logits
        
        predictions = torch.argmax(logits, dim=2)[0]
        predicted_labels_for_tokens = [id2label[p.item()] for p in predictions]

        # 对齐 subword 预测
        word_ids = tokenized_inputs.word_ids()
        predicted_tags = []
        current_word_id = -1
        for j, word_id in enumerate(word_ids):
            if word_id is not None and word_id != current_word_id:
                predicted_tags.append(predicted_labels_for_tokens[j])
                current_word_id = word_id

        # --- 6. 对比并打印错误 ---
        if len(predicted_tags) == len(true_tags):
            is_sent_correct = True
            for k in range(len(predicted_tags)):
                if predicted_tags[k] == true_tags[k]:
                    correct_predictions += 1
                else:
                    is_sent_correct = False
            
            if not is_sent_correct:
                total_errors += sum(1 for p, t in zip(predicted_tags, true_tags) if p != t)
                print(f"\nSentence: '{' '.join(original_tokens)}'")
                print("------------------------------------------")
                print(f"TOKEN         | TRUE TAG    | PREDICTED TAG")
                print("------------------------------------------")
                for token, true_tag, pred_tag in zip(original_tokens, true_tags, predicted_tags):
                    status = "  " if true_tag == pred_tag else "X"
                    print(f"{token:<14}| {true_tag:<12}| {pred_tag:<12} {status}")

    # --- 7. 打印总结 ---
    print("\n--- Summary ---")
    if total_tokens > 0:
        accuracy = correct_predictions / total_tokens
        print(f"Total tokens: {total_tokens}")
        print(f"Correct predictions: {correct_predictions}")
        print(f"Total errors: {total_tokens - correct_predictions}")
        print(f"Manual Accuracy Calculation: {accuracy:.2%}")
    else:
        print("No tokens were processed.")
    print("----------------------------------------")

if __name__ == "__main__":
    main()
