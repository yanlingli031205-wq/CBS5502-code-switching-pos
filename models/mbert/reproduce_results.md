
# Table 1: Overall Performance Evaluation

| System               |  Accuracy | Precision |   Recall  |     F1    |
| :------------------- | :-------: | :-------: | :-------: | :-------: |
| PyCantonese Baseline |    0.48   |   0.344   |   0.275   |   0.278   |
| + Rule-based patch   |   1.000   |   1.000   |   1.000   |   1.000   |
| BiLSTM-CRF           |   0.806   |   0.599   |   0.709   |   0.572   |
| **mBERT fine-tune**  | **0.908** | **0.849** | **0.816** | **0.853** |

### Table 2: Qualitative Analysis of Prediction Results

We used the final trained mBERT model to predict the three specified examples, with the following results:

| Sentence                     | Word   | Gold | PyCantonese | BiLSTM | **mBERT** |
| :--------------------------- | :----- | :--- | :---------: | :----: | :-------: |
| ...怕你 *miss* 了               | miss   | VERB |     NOUN    |  VERB  |  **VERB** |
| ...你们 *really* made our day! | really | ADV  |     NOUN    |  VERB  | **PROPN** |
| ...一百個 *Like* 讚你哋...         | Like   | NOUN |    PROPN    |  VERB  | **PROPN** |

**Analysis**: `mBERT` correctly predicted `miss`, but incorrectly identified `really` and `Like` as proper nouns (PROPN). This is consistent with the conclusion in the `README` that the model has difficulty distinguishing between nouns and proper nouns.
