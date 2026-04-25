
import os
import sys
import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification

# --- 1. 导入所有必要的模块和 lyl 的专家知识 ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from models.mbert.train_with_advanced_features import get_advanced_features

def predict_single_sentence(text, tokenizer, model, label_list):
    """对单个句子进行分词、特征注入和预测。"""
    
    # a. 使用基础的分词器（例如 Spacy 或 NLTK）先将句子切分为词
    #    为简单起见，我们这里直接用空格切分，这对于示例足够了
    tokens = text.split()
    
    # b. 为每个词注入高级特征
    featured_tokens = []
    for token in tokens:
        feature_tags = get_advanced_features(token, text)
        if feature_tags:
            featured_tokens.append(f"{token} {feature_tags}")
        else:
            featured_tokens.append(token)
            
    # c. 使用 mBERT 的 tokenizer 对特征化后的词元进行编码
    inputs = tokenizer(featured_tokens, return_tensors="pt", is_split_into_words=True, padding=True, truncation=True)
    
    # d. 模型预测
    with torch.no_grad():
        logits = model(**inputs).logits
        
    predictions = torch.argmax(logits, dim=2)
    
    # e. 解码预测结果
    predicted_token_class = [label_list[t.item()] for t in predictions[0]]
    
    # f. 将 subword 的预测结果对齐回原始词元
    word_ids = inputs.word_ids()
    previous_word_idx = None
    result = {}
    for i, word_idx in enumerate(word_ids):
        if word_idx is None or word_idx == previous_word_idx:
            continue
        # 我们只关心原始句子中的词
        original_token = tokens[word_idx]
        label = predicted_token_class[i]
        # 去掉 B- 或 I- 前缀
        label = label.split("-")[-1]
        result[original_token] = label
        previous_word_idx = word_idx
        
    return result

def main():
    model_dir = os.path.join(os.path.dirname(__file__), "mbert-advanced-features")
    
    # --- 1. 加载模型和 Tokenizer ---
    print("--- Loading Model and Tokenizer ---")
    model = AutoModelForTokenClassification.from_pretrained(model_dir)
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    label_list = model.config.id2label
    
    # --- 2. 定义要测试的句子 ---
    sentences = [
        "怕 你 miss 了",
        "你们 really made our day",
        "一百個 Like 讚 你哋"
    ]
    
    words_to_check = ["miss", "really", "Like"]

    # --- 3. 逐句预测 ---
    print("\n--- Starting Predictions ---")
    final_predictions = {}
    for sentence in sentences:
        predictions = predict_single_sentence(sentence, tokenizer, model, label_list)
        print(f"Sentence: '{sentence}'")
        print(f"Predictions: {predictions}")
        
        # 提取我们关心的词的预测结果
        for word in sentence.split():
            if word in words_to_check:
                final_predictions[word] = predictions.get(word, "N/A")

    # --- 4. 打印最终结果 ---
    print("\n--- mBERT Predictions for Table ---")
    for word, tag in final_predictions.items():
        print(f"Word: {word}, Predicted POS: {tag}")
        
if __name__ == "__main__":
    main()
