import argparse
import json
import os
import random
import re
import sys
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.metrics import accuracy_score, f1_score, precision_recall_fscore_support
from torch.utils.data import DataLoader, Dataset

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from models.rule_based.rule_based_tagger import (
    ADJ_LEXICON,
    ADV_LEXICON,
    INTJ_LEXICON,
    NEEDS_CONTEXT,
    NOUN_LEXICON,
    PROPN_LEXICON,
    VERB_LEXICON,
    X_LEXICON,
    _context_pos,
    read_conll as read_conll_full,
)


FEATURE_NAMES = [
    "in_intj_lexicon",
    "in_x_lexicon",
    "in_propn_lexicon",
    "in_verb_lexicon",
    "in_adj_lexicon",
    "in_adv_lexicon",
    "in_noun_lexicon",
    "is_all_caps",
    "is_digit",
    "has_hyphen",
    "is_init_cap",
    "needs_context_flag",
    "ctx_pred_is_noun",
    "ctx_pred_is_verb",
    "ctx_pred_is_adj",
]


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def load_splits(data_dir: str) -> Dict[str, List[Dict[str, List[str]]]]:
    def convert(path: str) -> List[Dict[str, List[str]]]:
        sents = read_conll_full(path)
        converted = []
        for sent in sents:
            converted.append(
                {
                    "sent_id": sent["sent_id"],
                    "text": sent["text"],
                    "tokens": [x[0] for x in sent["tokens"]],
                    "pos_tags": [x[1] for x in sent["tokens"]],
                }
            )
        return converted

    return {
        "train": convert(os.path.join(data_dir, "train.conll")),
        "dev": convert(os.path.join(data_dir, "dev.conll")),
        "test": convert(os.path.join(data_dir, "test.conll")),
    }


def build_vocabs(
    splits: Dict[str, List[Dict[str, List[str]]]]
) -> Tuple[Dict[str, int], Dict[str, int], Dict[str, int]]:
    words = set()
    chars = set()
    tags = set()
    for split_data in splits.values():
        for sent in split_data:
            tags.update(sent["pos_tags"])
            for token in sent["tokens"]:
                words.add(token.lower())
                chars.update(list(token))
    word2idx = {"<PAD>": 0, "<UNK>": 1}
    for w in sorted(words):
        word2idx[w] = len(word2idx)

    char2idx = {"<PAD>": 0, "<UNK>": 1}
    for c in sorted(chars):
        char2idx[c] = len(char2idx)

    tag2idx = {}
    for t in sorted(tags):
        tag2idx[t] = len(tag2idx)
    return word2idx, char2idx, tag2idx


def token_features(token: str, sentence_text: str) -> List[float]:
    t = token.lower()
    ctx_pred = _context_pos(token, sentence_text) if (t in NEEDS_CONTEXT and sentence_text) else None
    return [
        float(t in INTJ_LEXICON),
        float(t in X_LEXICON),
        float(t in PROPN_LEXICON),
        float(t in VERB_LEXICON),
        float(t in ADJ_LEXICON),
        float(t in ADV_LEXICON),
        float(t in NOUN_LEXICON),
        float(token.isupper() and len(token) > 1),
        float(token.isdigit()),
        float("-" in token),
        float(token[:1].isupper()),
        float(t in NEEDS_CONTEXT),
        float(ctx_pred == "NOUN"),
        float(ctx_pred == "VERB"),
        float(ctx_pred == "ADJ"),
    ]


@dataclass
class EncodedSample:
    token_ids: List[int]
    tag_ids: List[int]
    char_ids: List[List[int]]
    features: List[List[float]]
    tokens: List[str]
    tags: List[str]
    sentence_text: str


class ConllDataset(Dataset):
    def __init__(
        self,
        data: List[Dict[str, List[str]]],
        word2idx: Dict[str, int],
        char2idx: Dict[str, int],
        tag2idx: Dict[str, int],
    ) -> None:
        self.samples: List[EncodedSample] = []
        unk_word = word2idx["<UNK>"]
        unk_char = char2idx["<UNK>"]
        for sent in data:
            tokens = sent["tokens"]
            sentence_text = sent.get("text", "")
            token_ids = [word2idx.get(tok.lower(), unk_word) for tok in tokens]
            tag_ids = [tag2idx[tag] for tag in sent["pos_tags"]]
            char_ids = [[char2idx.get(ch, unk_char) for ch in tok] for tok in tokens]
            feats = [token_features(tok, sentence_text) for tok in tokens]
            self.samples.append(
                EncodedSample(
                    token_ids=token_ids,
                    tag_ids=tag_ids,
                    char_ids=char_ids,
                    features=feats,
                    tokens=tokens,
                    tags=sent["pos_tags"],
                    sentence_text=sentence_text,
                )
            )

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> EncodedSample:
        return self.samples[idx]


def collate_fn(batch: List[EncodedSample]) -> Dict[str, torch.Tensor]:
    batch_size = len(batch)
    lengths = [len(x.token_ids) for x in batch]
    max_len = max(lengths)
    max_char_len = max(len(chars) for sample in batch for chars in sample.char_ids)

    token_tensor = torch.zeros(batch_size, max_len, dtype=torch.long)
    tag_tensor = torch.zeros(batch_size, max_len, dtype=torch.long)
    mask = torch.zeros(batch_size, max_len, dtype=torch.bool)
    char_tensor = torch.zeros(batch_size, max_len, max_char_len, dtype=torch.long)
    feat_tensor = torch.zeros(batch_size, max_len, len(FEATURE_NAMES), dtype=torch.float32)

    tokens_raw: List[List[str]] = []
    tags_raw: List[List[str]] = []
    sentence_texts: List[str] = []

    for i, sample in enumerate(batch):
        l = len(sample.token_ids)
        token_tensor[i, :l] = torch.tensor(sample.token_ids, dtype=torch.long)
        tag_tensor[i, :l] = torch.tensor(sample.tag_ids, dtype=torch.long)
        mask[i, :l] = True
        feat_tensor[i, :l] = torch.tensor(sample.features, dtype=torch.float32)
        for j, chars in enumerate(sample.char_ids):
            char_tensor[i, j, : len(chars)] = torch.tensor(chars, dtype=torch.long)
        tokens_raw.append(sample.tokens)
        tags_raw.append(sample.tags)
        sentence_texts.append(sample.sentence_text)

    return {
        "tokens": token_tensor,
        "tags": tag_tensor,
        "mask": mask,
        "chars": char_tensor,
        "features": feat_tensor,
        "lengths": torch.tensor(lengths, dtype=torch.long),
        "tokens_raw": tokens_raw,
        "tags_raw": tags_raw,
        "sentence_texts": sentence_texts,
    }


class CRF(nn.Module):
    def __init__(self, num_tags: int) -> None:
        super().__init__()
        self.transitions = nn.Parameter(torch.randn(num_tags, num_tags))
        self.start_transitions = nn.Parameter(torch.randn(num_tags))
        self.end_transitions = nn.Parameter(torch.randn(num_tags))

    def forward(self, emissions: torch.Tensor, tags: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        numerator = self._score_sentence(emissions, tags, mask)
        denominator = self._compute_log_partition(emissions, mask)
        return torch.mean(denominator - numerator)

    def _score_sentence(self, emissions: torch.Tensor, tags: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        score = self.start_transitions[tags[:, 0]]
        score += emissions[:, 0].gather(1, tags[:, 0].unsqueeze(1)).squeeze(1)
        seq_len = emissions.size(1)
        for t in range(1, seq_len):
            trans = self.transitions[tags[:, t - 1], tags[:, t]]
            emit = emissions[:, t].gather(1, tags[:, t].unsqueeze(1)).squeeze(1)
            score += (trans + emit) * mask[:, t]
        lengths = mask.long().sum(dim=1) - 1
        last_tags = tags.gather(1, lengths.unsqueeze(1)).squeeze(1)
        score += self.end_transitions[last_tags]
        return score

    def _compute_log_partition(self, emissions: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        log_prob = self.start_transitions + emissions[:, 0]
        seq_len = emissions.size(1)
        for t in range(1, seq_len):
            score_t = log_prob.unsqueeze(2) + self.transitions.unsqueeze(0) + emissions[:, t].unsqueeze(1)
            next_log_prob = torch.logsumexp(score_t, dim=1)
            log_prob = torch.where(mask[:, t].unsqueeze(1), next_log_prob, log_prob)
        log_prob += self.end_transitions
        return torch.logsumexp(log_prob, dim=1)

    def decode(self, emissions: torch.Tensor, mask: torch.Tensor) -> List[List[int]]:
        score = self.start_transitions + emissions[:, 0]
        history: List[torch.Tensor] = []
        seq_len = emissions.size(1)
        for t in range(1, seq_len):
            next_score = score.unsqueeze(2) + self.transitions.unsqueeze(0)
            best_score, best_path = next_score.max(dim=1)
            best_score += emissions[:, t]
            score = torch.where(mask[:, t].unsqueeze(1), best_score, score)
            history.append(best_path)

        score += self.end_transitions
        best_last_tag = score.argmax(dim=1)
        lengths = mask.long().sum(dim=1)
        paths = []
        for i in range(emissions.size(0)):
            seq_end = lengths[i].item() - 1
            tag = best_last_tag[i].item()
            path = [tag]
            for hist_t in reversed(history[:seq_end]):
                tag = hist_t[i][tag].item()
                path.append(tag)
            paths.append(list(reversed(path)))
        return paths


class BiLSTMCRF(nn.Module):
    def __init__(
        self,
        vocab_size: int,
        char_vocab_size: int,
        num_tags: int,
        word_emb_dim: int = 100,
        char_emb_dim: int = 32,
        char_hidden_dim: int = 32,
        feat_hidden_dim: int = 32,
        lstm_hidden_dim: int = 128,
        dropout: float = 0.5,
        pad_idx: int = 0,
    ) -> None:
        super().__init__()
        self.word_emb = nn.Embedding(vocab_size, word_emb_dim, padding_idx=pad_idx)
        self.char_emb = nn.Embedding(char_vocab_size, char_emb_dim, padding_idx=pad_idx)
        self.char_lstm = nn.LSTM(char_emb_dim, char_hidden_dim // 2, batch_first=True, bidirectional=True)
        self.feature_proj = nn.Sequential(
            nn.Linear(len(FEATURE_NAMES), feat_hidden_dim),
            nn.ReLU(),
        )
        encoder_in_dim = word_emb_dim + char_hidden_dim + feat_hidden_dim
        self.encoder = nn.LSTM(
            encoder_in_dim,
            lstm_hidden_dim // 2,
            num_layers=1,
            bidirectional=True,
            batch_first=True,
        )
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(lstm_hidden_dim, num_tags)
        self.crf = CRF(num_tags)

    def _encode_chars(self, chars: torch.Tensor) -> torch.Tensor:
        bsz, seq_len, max_char_len = chars.size()
        flat_chars = chars.view(bsz * seq_len, max_char_len)
        char_mask = flat_chars.ne(0)
        lengths = char_mask.long().sum(dim=1)
        lengths = torch.clamp(lengths, min=1)
        emb = self.char_emb(flat_chars)
        packed = nn.utils.rnn.pack_padded_sequence(emb, lengths.cpu(), batch_first=True, enforce_sorted=False)
        _, (h_n, _) = self.char_lstm(packed)
        char_repr = torch.cat([h_n[-2], h_n[-1]], dim=1)
        return char_repr.view(bsz, seq_len, -1)

    def emissions(self, tokens: torch.Tensor, chars: torch.Tensor, feats: torch.Tensor) -> torch.Tensor:
        word_repr = self.word_emb(tokens)
        char_repr = self._encode_chars(chars)
        feat_repr = self.feature_proj(feats)
        x = torch.cat([word_repr, char_repr, feat_repr], dim=-1)
        x, _ = self.encoder(x)
        x = self.dropout(x)
        return self.classifier(x)

    def loss(self, tokens: torch.Tensor, chars: torch.Tensor, feats: torch.Tensor, tags: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        emissions = self.emissions(tokens, chars, feats)
        return self.crf(emissions, tags, mask)

    def predict(self, tokens: torch.Tensor, chars: torch.Tensor, feats: torch.Tensor, mask: torch.Tensor) -> List[List[int]]:
        emissions = self.emissions(tokens, chars, feats)
        return self.crf.decode(emissions, mask)


def compute_metrics(y_true: List[str], y_pred: List[str]) -> Dict[str, object]:
    labels = sorted(list(set(y_true)))
    precision, recall, f1, support = precision_recall_fscore_support(y_true, y_pred, labels=labels, zero_division=0)
    per_label = {}
    for i, label in enumerate(labels):
        per_label[label] = {
            "precision": round(float(precision[i]), 4),
            "recall": round(float(recall[i]), 4),
            "f1": round(float(f1[i]), 4),
            "support": int(support[i]),
        }
    return {
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "macro_f1": round(float(f1_score(y_true, y_pred, average="macro", zero_division=0)), 4),
        "weighted_f1": round(float(f1_score(y_true, y_pred, average="weighted", zero_division=0)), 4),
        "per_label": per_label,
        "num_tokens": len(y_true),
    }


def rule_based_predict_with_confidence(token: str, sentence_text: str) -> Tuple[str, bool]:
    tok_low = token.lower()

    if tok_low in INTJ_LEXICON:
        return "INTJ", True

    if tok_low in X_LEXICON:
        return "X", True
    if re.match(r"^x+d+$", tok_low) and len(token) >= 2:
        return "X", True

    if tok_low in PROPN_LEXICON:
        return "PROPN", True

    if re.match(r"^[A-Z]{2,}$", token):
        if tok_low in ADJ_LEXICON:
            return "ADJ", True
        if tok_low in VERB_LEXICON:
            return "VERB", True
        if tok_low in ADV_LEXICON:
            return "ADV", True
        if tok_low in NOUN_LEXICON:
            return "NOUN", True
        return "PROPN", True

    if token.isdigit():
        return "NUM", True

    if "-" in token:
        return "NOUN", True

    if tok_low in NEEDS_CONTEXT and sentence_text:
        ctx = _context_pos(token, sentence_text)
        if ctx:
            return ctx, True

    if tok_low in VERB_LEXICON:
        return "VERB", True
    if tok_low in ADJ_LEXICON:
        return "ADJ", True
    if tok_low in ADV_LEXICON:
        return "ADV", True
    if tok_low in NOUN_LEXICON:
        return "NOUN", True

    if token[:1].isupper():
        return "PROPN", True

    return "NOUN", False


def apply_hybrid_postprocess(token: str, sentence_text: str, pred_tag: str) -> str:
    rule_tag, confident = rule_based_predict_with_confidence(token, sentence_text)
    if confident:
        return rule_tag
    return pred_tag


def evaluate_model(
    model: BiLSTMCRF,
    loader: DataLoader,
    idx2tag: Dict[int, str],
    device: torch.device,
    use_hybrid_postprocess: bool = False,
) -> Tuple[Dict[str, object], List[List[str]], List[List[str]]]:
    model.eval()
    all_gold: List[str] = []
    all_pred: List[str] = []
    sent_tokens: List[List[str]] = []
    sent_preds: List[List[str]] = []
    with torch.no_grad():
        for batch in loader:
            tokens = batch["tokens"].to(device)
            chars = batch["chars"].to(device)
            feats = batch["features"].to(device)
            mask = batch["mask"].to(device)
            predictions = model.predict(tokens, chars, feats, mask)
            for i, pred_ids in enumerate(predictions):
                gold_seq = batch["tags_raw"][i]
                pred_seq = [idx2tag[idx] for idx in pred_ids]
                if use_hybrid_postprocess:
                    sent_text = batch["sentence_texts"][i]
                    pred_seq = [
                        apply_hybrid_postprocess(tok, sent_text, pred)
                        for tok, pred in zip(batch["tokens_raw"][i], pred_seq)
                    ]
                all_gold.extend(gold_seq)
                all_pred.extend(pred_seq)
                sent_tokens.append(batch["tokens_raw"][i])
                sent_preds.append(pred_seq)
    return compute_metrics(all_gold, all_pred), sent_tokens, sent_preds


def save_json(path: str, data: Dict[str, object]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_pred_conll(path: str, tokens: List[List[str]], preds: List[List[str]]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for token_seq, pred_seq in zip(tokens, preds):
            for token, pred in zip(token_seq, pred_seq):
                f.write(f"{token}\t{pred}\n")
            f.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Optimized BiLSTM-CRF with lexicon and char features.")
    parser.add_argument("--data-dir", default=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data")))
    parser.add_argument("--output-dir", default=os.path.join(os.path.dirname(__file__), "results"))
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--patience", type=int, default=12)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=8e-4)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--word-emb-dim", type=int, default=100)
    parser.add_argument("--char-emb-dim", type=int, default=32)
    parser.add_argument("--char-hidden-dim", type=int, default=32)
    parser.add_argument("--feat-hidden-dim", type=int, default=32)
    parser.add_argument("--lstm-hidden-dim", type=int, default=128)
    parser.add_argument("--dropout", type=float, default=0.5)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--use-hybrid-postprocess", action="store_true")
    args = parser.parse_args()

    set_seed(args.seed)
    os.makedirs(args.output_dir, exist_ok=True)

    splits = load_splits(args.data_dir)
    word2idx, char2idx, tag2idx = build_vocabs(splits)
    idx2tag = {idx: tag for tag, idx in tag2idx.items()}

    train_ds = ConllDataset(splits["train"], word2idx, char2idx, tag2idx)
    dev_ds = ConllDataset(splits["dev"], word2idx, char2idx, tag2idx)
    test_ds = ConllDataset(splits["test"], word2idx, char2idx, tag2idx)

    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True, collate_fn=collate_fn)
    dev_loader = DataLoader(dev_ds, batch_size=args.batch_size, shuffle=False, collate_fn=collate_fn)
    test_loader = DataLoader(test_ds, batch_size=args.batch_size, shuffle=False, collate_fn=collate_fn)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = BiLSTMCRF(
        vocab_size=len(word2idx),
        char_vocab_size=len(char2idx),
        num_tags=len(tag2idx),
        word_emb_dim=args.word_emb_dim,
        char_emb_dim=args.char_emb_dim,
        char_hidden_dim=args.char_hidden_dim,
        feat_hidden_dim=args.feat_hidden_dim,
        lstm_hidden_dim=args.lstm_hidden_dim,
        dropout=args.dropout,
    ).to(device)

    optimizer = optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="max", factor=0.5, patience=4)

    best_dev_f1 = -1.0
    patience_counter = 0
    best_model_path = os.path.join(args.output_dir, "best_model.pt")
    history: List[Dict[str, float]] = []

    for epoch in range(1, args.epochs + 1):
        model.train()
        total_loss = 0.0
        for batch in train_loader:
            tokens = batch["tokens"].to(device)
            chars = batch["chars"].to(device)
            feats = batch["features"].to(device)
            tags = batch["tags"].to(device)
            mask = batch["mask"].to(device)
            optimizer.zero_grad()
            loss = model.loss(tokens, chars, feats, tags, mask)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), max_norm=5.0)
            optimizer.step()
            total_loss += loss.item()

        avg_train_loss = total_loss / max(1, len(train_loader))
        dev_metrics, _, _ = evaluate_model(
            model, dev_loader, idx2tag, device, use_hybrid_postprocess=args.use_hybrid_postprocess
        )
        dev_f1 = float(dev_metrics["weighted_f1"])
        scheduler.step(dev_f1)

        current_lr = optimizer.param_groups[0]["lr"]
        history.append(
            {
                "epoch": epoch,
                "train_loss": round(avg_train_loss, 6),
                "dev_accuracy": float(dev_metrics["accuracy"]),
                "dev_weighted_f1": dev_f1,
                "lr": float(current_lr),
            }
        )
        print(
            f"[Epoch {epoch:02d}] train_loss={avg_train_loss:.4f} "
            f"dev_acc={dev_metrics['accuracy']:.4f} dev_weighted_f1={dev_f1:.4f} lr={current_lr:.6f}"
        )

        if dev_f1 > best_dev_f1:
            best_dev_f1 = dev_f1
            patience_counter = 0
            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "word2idx": word2idx,
                    "char2idx": char2idx,
                    "tag2idx": tag2idx,
                    "feature_names": FEATURE_NAMES,
                    "args": vars(args),
                },
                best_model_path,
            )
        else:
            patience_counter += 1
            if patience_counter >= args.patience:
                print(f"Early stopping triggered at epoch {epoch}.")
                break

    checkpoint = torch.load(best_model_path, map_location=device)
    model.load_state_dict(checkpoint["model_state_dict"])

    train_metrics, _, _ = evaluate_model(
        model, train_loader, idx2tag, device, use_hybrid_postprocess=args.use_hybrid_postprocess
    )
    dev_metrics, _, _ = evaluate_model(
        model, dev_loader, idx2tag, device, use_hybrid_postprocess=args.use_hybrid_postprocess
    )
    test_metrics, test_tokens, test_preds = evaluate_model(
        model, test_loader, idx2tag, device, use_hybrid_postprocess=args.use_hybrid_postprocess
    )

    save_json(os.path.join(args.output_dir, "train_metrics.json"), train_metrics)
    save_json(os.path.join(args.output_dir, "dev_metrics.json"), dev_metrics)
    save_json(os.path.join(args.output_dir, "test_metrics.json"), test_metrics)
    save_json(
        os.path.join(args.output_dir, "training_history.json"),
        {
            "history": history,
            "best_dev_weighted_f1": best_dev_f1,
            "feature_names": FEATURE_NAMES,
            "use_hybrid_postprocess": args.use_hybrid_postprocess,
        },
    )
    save_pred_conll(os.path.join(args.output_dir, "test_pred.conll"), test_tokens, test_preds)

    print("=== Final Metrics (Best Dev Model) ===")
    print(f"Train: acc={train_metrics['accuracy']:.4f}, weighted_f1={train_metrics['weighted_f1']:.4f}")
    print(f"Dev:   acc={dev_metrics['accuracy']:.4f}, weighted_f1={dev_metrics['weighted_f1']:.4f}")
    print(f"Test:  acc={test_metrics['accuracy']:.4f}, weighted_f1={test_metrics['weighted_f1']:.4f}")
    print(f"Saved artifacts to: {args.output_dir}")


if __name__ == "__main__":
    main()
