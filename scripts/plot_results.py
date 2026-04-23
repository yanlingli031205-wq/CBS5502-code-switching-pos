
import matplotlib.pyplot as plt
import numpy as np
import os

def main():
    # --- 1. 定义所有模型的性能数据 ---
    models = [
        "PyCantonese (Baseline)",
        "mBERT (Baseline)",
        "mBERT + Lexicon Feat.",
        "mBERT + Advanced Feat.",
        "Rule-based (lyl)"
    ]
    f1_scores = [0.49, 0.601, 0.827, 0.853, 1.0]
    accuracy_scores = [0.4886, 0.7347, 0.8878, 0.9082, 1.0]

    # --- 2. 创建图表 ---
    x = np.arange(len(models))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots(figsize=(12, 8))
    
    rects1 = ax.bar(x - width/2, f1_scores, width, label='F1 Score', color='skyblue')
    rects2 = ax.bar(x + width/2, accuracy_scores, width, label='Accuracy', color='lightcoral')

    # --- 3. 添加文本、标签和标题 ---
    ax.set_ylabel('Scores')
    ax.set_title('Model Performance Comparison for Code-Switching POS Tagging')
    ax.set_xticks(x)
    ax.set_xticklabels(models, rotation=20, ha="right")
    ax.legend()
    ax.set_ylim(0, 1.1)

    def autolabel(rects):
        """在每个柱子上方附加一个文本标签。"""
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.3f}',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')

    autolabel(rects1)
    autolabel(rects2)

    fig.tight_layout()

    # --- 4. 保存图表 ---
    output_dir = os.path.join(os.path.dirname(__file__), "..", "report", "figures")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "model_comparison.png")
    
    plt.savefig(output_path)
    print(f"Chart saved to: {output_path}")

if __name__ == '__main__':
    main()
