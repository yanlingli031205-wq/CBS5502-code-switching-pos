#

| System               |  Accuracy | Precision |   Recall  |     F1    |
| :------------------- | :-------: | :-------: | :-------: | :-------: |
| PyCantonese Baseline |    0.48   |   0.344   |   0.275   |   0.278   |
| + Rule-based patch   |   1.000   |   1.000   |   1.000   |   1.000   |
| BiLSTM-CRF           |   0.806   |   0.599   |   0.709   |   0.572   |
| **mBERT fine-tune**  | **0.908** | **0.849** | **0.816** | **0.853** |

### 表 2：定性分析预测结果

我们使用最终训练好的 mBERT 模型对指定的三个例子进行了预测，结果如下：

| Sentence                     | Word   | Gold | PyCantonese | BiLSTM | **mBERT** |
| :--------------------------- | :----- | :--- | :---------: | :----: | :-------: |
| ...怕你 *miss* 了               | miss   | VERB |     NOUN    |  VERB  |  **VERB** |
| ...你们 *really* made our day! | really | ADV  |     NOUN    |  VERB  | **PROPN** |
| ...一百個 *Like* 讚你哋...         | Like   | NOUN |    PROPN    |  VERB  | **PROPN** |

**分析**: `mBERT` 正确预测了 `miss`，但将 `really` 和 `Like` 错误地识别为了专有名词（PROPN），这与 `README` 中关于模型难以区分名词和专有名词的结论一致。

##

