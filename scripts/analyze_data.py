
import os
import sys
from collections import Counter

# 将项目根目录添加到sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.io import read_conll

def analyze_file(filepath):
    if not os.path.exists(filepath):
        return 0, 0, Counter()
    sents = read_conll(filepath)
    num_sents = len(sents)
    num_tokens = sum(len(s["tokens"]) for s in sents)
    tag_counts = Counter(tag for s in sents for tag in s["pos_tags"])
    return num_sents, num_tokens, tag_counts

if __name__ == "__main__":
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
    
    train_sents, train_tokens, train_tags = analyze_file(os.path.join(data_dir, "train.conll"))
    dev_sents, dev_tokens, _ = analyze_file(os.path.join(data_dir, "dev.conll"))
    test_sents, test_tokens, _ = analyze_file(os.path.join(data_dir, "test.conll"))

    print("--- Dataset Analysis ---")
    print(f"Train set: {train_sents} sentences, {train_tokens} tokens")
    print(f"Dev set:   {dev_sents} sentences, {dev_tokens} tokens")
    print(f"Test set:  {test_sents} sentences, {test_tokens} tokens")
    print("------------------------\n")
    
    print("--- Tag Distribution in Training Set ---")
    total_tags = sum(train_tags.values())
    for tag, count in train_tags.most_common():
        print(f"{tag:<10} | {count:<5} | {count/total_tags:.2%}")
    print("----------------------------------------")
