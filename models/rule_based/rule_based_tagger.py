#!/usr/bin/env python3
"""
Rule-based POS Tagger for Cantonese-English Code-Switching
CBS5502 Group Project — Step 4a

Author : liyanling (lyl)
Date   : 2026-04-22

Design : Cascaded priority rules (lexicon + Cantonese context patterns)

Priority order
  1.  INTJ lexicon
  2.  X lexicon  +  XD emoticon regex
  3.  PROPN lexicon  (known brands / places / person names)
  4.  ALL-CAPS pattern  → PROPN  (e.g. BBC, ABC, UFO)
  5.  Digit pattern  → NUM
  6.  Hyphenated compound  → NOUN  (e.g. part-time)
  7.  Context rules for ambiguous tokens  (reads Cantonese sentence text)
  8.  VERB lexicon
  9.  ADJ lexicon
 10.  ADV lexicon
 11.  NOUN lexicon
 12.  Initial capital  → PROPN  (unknown capitalised words)
 13.  Default  → NOUN

Usage
  # Evaluate on test set (prints metrics to stdout, saves JSON):
  python rule_based_tagger.py --input ../../data/test.conll

  # Also write CoNLL-format prediction file:
  python rule_based_tagger.py --input ../../data/test.conll --output results/test_pred.conll

  # Evaluate on all three splits:
  python rule_based_tagger.py --input ../../data/train.conll
  python rule_based_tagger.py --input ../../data/dev.conll
  python rule_based_tagger.py --input ../../data/test.conll
"""

import re
import sys
import json
import argparse
from pathlib import Path
from collections import Counter


# ══════════════════════════════════════════════════════════════════
# LEXICONS
# All entries stored lowercase; token is lowercased before lookup.
# Source: manual error analysis of gold_standard annotation (Step 3)
# ══════════════════════════════════════════════════════════════════

# ── Priority 1 ─────────────────────────────────────────────────────
INTJ_LEXICON = {
    # Laughter / reaction
    'haha', 'hahaha', 'hahahaha', 'lol', 'omg', 'omgggg', 'omggggg',
    'wow', 'wah', 'wa',
    # Cheering / encouragement
    'fighting', 'cheers', 'congrats', 'congratulations',
    'salute', 'bravo', 'welcome', 'bbg', 'tt',
    # Greetings
    'hi', 'hello', 'bye', 'goodbye',
    # Other exclamations
    'yay', 'ok', 'thx',
    # Context-specific: "omg", variations handled by above
}

# ── Priority 2 ─────────────────────────────────────────────────────
X_LEXICON = {
    # Cantonese discourse particles (romanised)
    'lor', 'la', 'wor', 'ar', 'lar', 'loh', 'ge', 'geh', 'lah', 'leh',
    # Internet abbreviations
    'btw', 'pls', 'etc', 'ootd', 'cls',
    # Cantonese slang / non-English tokens
    'hea', 'jeng', 'dingding', 'ding',
    # HK internet emoticons / tokens
    'fd', 'cos', 'fdz', 'der', 'lee', 'yr',  # fd = 表情符号（非 abbreviation）
    # Single letters used as Cantonese particles / emoticon fragments
    'd', 'p', 'y', 'x', 'w', 's',
}
# XD emoticon pattern (xd, xdd, xddd, …) handled by regex in predict_pos()

# ── Priority 3 ─────────────────────────────────────────────────────
PROPN_LEXICON = {
    # Tech platforms & product brands
    'apple', 'iphone', 'ipad', 'mac', 'macbook',
    'youtube', 'ig', 'instagram', 'facebook', 'tiktok', 'twitter',
    'threads', 'google', 'netflix', 'amazon', 'spotify',
    'tesla', 'uber', 'airbnb', 'microsoft', 'windows', 'android',
    'whatsapp', 'telegram', 'yt',
    'mcdonald', 'mcdonalds', 'starbucks', 'ikea', 'hermes',
    'maybelline', 'radius', 'ive', 'lalaport', 'gundam', 'namco',
    'gantogelato', 'bakehouse', 'vission',
    # Places & languages
    'singapore', 'london', 'paris', 'japan', 'taiwan',
    'cantonese', 'french', 'lima', 'miraflores', 'larcomar',
    # Person names appearing in corpus
    'trump', 'elon', 'musk', 'obama', 'donald',
    'ariel', 'torres', 'kiki', 'jenn', 'jen',
    'grace', 'megan', 'hilary', 'hebe', 'wing',
    'guang', 'hana', 'pu', 'jennn',
    # Product model: "apple watch" → both tokens tagged PROPN in gold
    'watch',
    # Other proper names in corpus
    'youtuber', 'romansh', 'umass', 'tifa', 'graddin',
}

# ── Priority 8 ─────────────────────────────────────────────────────
VERB_LEXICON = {
    # Social media & digital actions
    'post', 'repost', 'share', 'follow', 'subscribe', 'subscribed',
    'upload', 'download', 'update', 'delete', 'bookmark',
    'mute', 'like', 'dislike', 'sub',
    # Communication & general action verbs
    'call', 'make', 'get', 'go', 'come', 'see', 'know', 'say', 'use',
    'keep', 'miss', 'try', 'want', 'need', 'fly', 'loop', 'deal',
    'learn', 'propose', 'appreciate', 'register', 'compare', 'approve',
    'translate', 'interview', 'book', 'copy', 'plan', 'gel', 'admire',
    'expect', 'cheer', 'give', 'run', 'buy', 'sell',
    # Verbs frequently mistagged in PyCantonese (from error analysis)
    'delay', 'quit', 'claim', 'mark', 'point', 'cam',
    'love', 'support', 'made', 'enjoy', 'up',
    # Inflected / derived verb forms
    'looks', 'knowing', 'enjoyed', 'missed', 'glowing',
    'thanks', 'thank',       # "thanks for sharing" → VERB in gold standard
    'ko',                    # KO啲毛毛 → VERB
    'playback', 'po', 'planning', 'keeping', 'tick',
}

# ── Priority 9 ─────────────────────────────────────────────────────
ADJ_LEXICON = {
    # Appearance & quality
    'cute', 'nice', 'cool', 'hot', 'warm', 'cold', 'clean', 'clear',
    'gorgeous', 'beautiful', 'pretty', 'ugly', 'dirty',
    'good', 'bad', 'great', 'perfect', 'fun', 'funny',
    'huge', 'big', 'small', 'tall', 'short', 'cheap', 'expensive',
    'fit', 'better', 'best', 'local', 'chill', 'dramatic',
    'proud', 'inspiring', 'inspired',
    'different', 'final', 'true', 'sad', 'happy', 'sweet', 'lovely',
    # Code-switching specific adjectives
    'native', 'chur', 'facial',   # "facial expression" → facial = ADJ
    'much',                        # "so much" → much = ADV, but tagged ADJ in context
    # Additional from corpus
    'aesthetic', 'positive', 'friendly', 'online', 'grand',
    'detailed', 'social', 'jealous', 'underrated', 'abstract',
    'high', 'crazy', 'soft', 'full', 'first',
    'american', 'chinese',
    'non',                         # "non native speaker" → non = ADJ
    'ghost',                       # "ghost jobs" → ADJ
    'fresh', 'sure',
}

# ── Priority 10 ────────────────────────────────────────────────────
ADV_LEXICON = {
    'really', 'very', 'never', 'just', 'yet', 'anyway', 'besides',
    'already', 'still', 'also', 'even', 'only', 'so', 'well', 'long',
    'actually',
}

# ── Priority 11 ────────────────────────────────────────────────────
NOUN_LEXICON = {
    # Body & beauty
    'lip', 'stick', 'lipstick', 'foundation', 'colour', 'color', 'con', 'wig',
    # Family & people
    'mami', 'mom', 'mum', 'dad', 'daddy', 'uncle', 'aunty', 'auntie',
    'sister', 'brother', 'fan', 'fans', 'friend', 'boss', 'editor', 'staff',
    # Media & tech
    'video', 'clip', 'vlog', 'channel', 'app', 'banner', 'link',
    'intro', 'story', 'photo', 'pic', 'content', 'reel', 'reels',
    'comment', 'comments', 'view', 'booking', 'setup',
    # Abstract concepts
    'speech', 'way', 'expression', 'feel', 'heart', 'vibe',
    'logic', 'topic', 'detail', 'details', 'brand',
    'language', 'accent', 'speaker', 'level', 'type', 'style',
    'look', 'point', 'respect', 'support', 'follow',
    # Spaces & physical objects
    'ball', 'outlet', 'center', 'centre', 'sport', 'map', 'room', 'house',
    'hotel', 'party', 'event', 'tour', 'kitchen', 'gym',
    'programmer', 'chicken', 'picotin', 'base', 'board', 'cam',
    # Food & social
    'bonus', 'day', 'man', 'band', 'shot', 'jam',
    'casino', 'lunch', 'ice', 'butter', 'lamb', 'mutton',
    # Gerunds used as nouns in code-switching context
    'sharing', 'planning', 'booking', 'shopping', 'nursing',
    # Misc from corpus
    'collection', 'deck', 'frame', 'part', 'parts',
    'round', 'bling', 'bakery', 'playhouse', 'series', 'thread', 'logo',
    'top', 'key', 'din', 'grad', 'side', 'accessory',
    'major', 'bar', 'workshop', 'contractor', 'rank', 'team', 'pack',
    'school', 'outfit', 'quality', 'sis', 'chemistry', 'relationship',
    'immigration', 'times', 'five', 'one',
}

# ══════════════════════════════════════════════════════════════════
# CONTEXT RULES
# Applied ONLY to tokens in NEEDS_CONTEXT before lexicon lookup.
# Uses surrounding Cantonese characters in the original sentence.
# ══════════════════════════════════════════════════════════════════

# Tokens where Cantonese context should override lexicon defaults
NEEDS_CONTEXT = {
    'like', 'post', 'follow', 'love', 'support',
    'share', 'update', 'point',
}

# Cantonese classifiers/determiners that precede nouns
#   e.g. "一百個 Like" → Like = NOUN
CANTO_CLASSIFIERS = set('個啲嗰種件幅隻條張棟幢間層')

# Cantonese possessive particles that follow a modifier before a noun
#   e.g. "嗰種feel" / "佢嘅feel" → feel = NOUN
CANTO_POSSESSIVE = set('嘅既')

# Cantonese object pronouns that follow transitive verbs
#   e.g. "support你地" → support = VERB
CANTO_PRONOUNS = set('你我佢')

# Cantonese modal / aspect markers that precede verbs
#   e.g. "有follow" / "幫手share" → VERB
CANTO_MODALS = ['去', '想', '要', '會', '有', '幫', '可', '係', '唔']

# Cantonese degree adverbs that precede adjectives
#   e.g. "好chill" / "好true" → ADJ
CANTO_DEGREE = ['好', '幾', '非常', '真係', '超', '極', '最']


def _get_context(token: str, sentence_text: str, window: int = 10):
    """
    Return (before_str, after_str) for the token in sentence_text.
    Trailing / leading whitespace is stripped so the last / first
    character reflects an actual Cantonese or English character.
    """
    idx = sentence_text.find(token)
    if idx == -1:
        idx = sentence_text.lower().find(token.lower())
    if idx == -1:
        return '', ''

    before_str = sentence_text[max(0, idx - window): idx].rstrip()
    after_str  = sentence_text[idx + len(token):].lstrip()
    return before_str, after_str


def _context_pos(token: str, sentence_text: str):
    """
    Apply Cantonese context rules; return POS string or None.

    Rule priority:
      C1. Classifier directly before  → NOUN   ("一百個 Like")
      C2. Cantonese pronoun after     → VERB   ("support你地")
      C2b.English pronoun after       → VERB   ("love it!!")
      C3. Possessive 嘅/既 before     → NOUN   ("嗰種feel")
      C4. Modal character in window   → VERB   ("有follow", "幫手share")
      C5. Degree adverb ends window   → ADJ    ("好chill")
      C6. 要/去 directly before       → VERB   ("要Like")
    """
    before_str, after_str = _get_context(token, sentence_text)

    # C1: classifier immediately before → NOUN
    if before_str and before_str[-1] in CANTO_CLASSIFIERS:
        return 'NOUN'

    # C2: Cantonese object pronoun after → VERB
    if after_str and after_str[0] in CANTO_PRONOUNS:
        return 'VERB'

    # C2b: English object pronoun after → VERB
    if after_str and after_str.lower().startswith(
            ('it ', 'it!', 'it,', 'it.', 'them', 'him ', 'her ')):
        return 'VERB'

    # C3: possessive 嘅/既 before → NOUN
    if before_str and before_str[-1] in CANTO_POSSESSIVE:
        return 'NOUN'

    # C4: modal character anywhere in before window → VERB
    for modal in CANTO_MODALS:
        if modal in before_str:
            return 'VERB'

    # C5: degree adverb ends before window → ADJ
    for adv in CANTO_DEGREE:
        if before_str.endswith(adv):
            return 'ADJ'

    # C6: 要/去 directly before → VERB  (subset of C4, kept explicit)
    if before_str and before_str[-1] in '要去':
        return 'VERB'

    return None


# ══════════════════════════════════════════════════════════════════
# PREDICTION
# ══════════════════════════════════════════════════════════════════

def predict_pos(token: str, sentence_text: str = '') -> str:
    """
    Predict the Universal POS tag for an English token.

    Parameters
    ----------
    token         : English token (original casing preserved)
    sentence_text : Full Cantonese-English sentence (enables context rules)

    Returns
    -------
    Universal POS tag string
    """
    tok_low = token.lower()

    # ── 1. INTJ lexicon ─────────────────────────────────────────
    if tok_low in INTJ_LEXICON:
        return 'INTJ'

    # ── 2. X lexicon + XD emoticon pattern ──────────────────────
    if tok_low in X_LEXICON:
        return 'X'
    if re.match(r'^x+d+$', tok_low) and len(token) >= 2:
        return 'X'

    # ── 3. Known proper nouns ────────────────────────────────────
    if tok_low in PROPN_LEXICON:
        return 'PROPN'

    # ── 4. All-caps abbreviation (≥ 2 letters) → PROPN ──────────
    #    But if the lowercase form is a known word (ADJ/VERB/ADV/NOUN),
    #    the caps are stylistic emphasis — return the word's real POS first.
    #    E.g. "TRUE" → ADJ, "FEEL" → NOUN, but "BBC" / "UFO" → PROPN.
    if re.match(r'^[A-Z]{2,}$', token):
        if tok_low in ADJ_LEXICON:
            return 'ADJ'
        if tok_low in VERB_LEXICON:
            return 'VERB'
        if tok_low in ADV_LEXICON:
            return 'ADV'
        if tok_low in NOUN_LEXICON:
            return 'NOUN'
        return 'PROPN'

    # ── 5. Digit-only token → NUM ────────────────────────────────
    if re.match(r'^\d+$', token):
        return 'NUM'

    # ── 6. Hyphenated compound → NOUN  (e.g. part-time) ─────────
    if '-' in token:
        return 'NOUN'

    # ── 7. Context rules for ambiguous tokens ───────────────────
    if tok_low in NEEDS_CONTEXT and sentence_text:
        ctx = _context_pos(token, sentence_text)
        if ctx:
            return ctx

    # ── 8. VERB lexicon ──────────────────────────────────────────
    if tok_low in VERB_LEXICON:
        return 'VERB'

    # ── 9. ADJ lexicon ───────────────────────────────────────────
    if tok_low in ADJ_LEXICON:
        return 'ADJ'

    # ── 10. ADV lexicon ──────────────────────────────────────────
    if tok_low in ADV_LEXICON:
        return 'ADV'

    # ── 11. NOUN lexicon ─────────────────────────────────────────
    if tok_low in NOUN_LEXICON:
        return 'NOUN'

    # ── 12. Initial capital → PROPN  (unknown capitalised word) ──
    if token[0].isupper():
        return 'PROPN'

    # ── 13. Default fallback ─────────────────────────────────────
    return 'NOUN'


# ══════════════════════════════════════════════════════════════════
# CoNLL I/O
# ══════════════════════════════════════════════════════════════════

def read_conll(filepath: str):
    """
    Read a CoNLL-format file.

    Expected format per sentence:
        # sent_id = <id>
        # text = <full sentence>
        <token>\\t<gold_pos>
        ...
        <blank line>

    Returns
    -------
    List of dicts, each with keys:
        sent_id (str), text (str), tokens (list of (token, gold_pos))
    """
    sentences = []
    current = {'sent_id': None, 'text': '', 'tokens': []}

    with open(filepath, encoding='utf-8') as fh:
        for raw_line in fh:
            line = raw_line.rstrip('\n')

            if line.startswith('# sent_id'):
                # Flush previous sentence if it has tokens
                if current['tokens']:
                    sentences.append(current)
                current = {'sent_id': None, 'text': '', 'tokens': []}
                current['sent_id'] = line.split('=', 1)[1].strip()

            elif line.startswith('# text'):
                current['text'] = line.split('=', 1)[1].strip()

            elif line and not line.startswith('#'):
                parts = line.split('\t')
                if len(parts) == 2:
                    current['tokens'].append((parts[0], parts[1]))

    if current['tokens']:
        sentences.append(current)

    return sentences


def write_conll(sentences_with_preds, filepath: str):
    """Write predicted labels to CoNLL format."""
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as fh:
        for sent in sentences_with_preds:
            fh.write(f"# sent_id = {sent['sent_id']}\n")
            fh.write(f"# text = {sent['text']}\n")
            for tok_info in sent['tokens']:
                fh.write(f"{tok_info['token']}\t{tok_info['pred']}\n")
            fh.write('\n')


# ══════════════════════════════════════════════════════════════════
# EVALUATION
# ══════════════════════════════════════════════════════════════════

def evaluate(sentences):
    """
    Run rule-based predictions and compute evaluation metrics.

    Returns
    -------
    dict with keys:
        accuracy, macro_f1, weighted_f1, class_metrics,
        total, correct, results, gold, pred
    """
    all_gold, all_pred = [], []
    results = []

    for sent in sentences:
        sent_result = {
            'sent_id': sent['sent_id'],
            'text':    sent['text'],
            'tokens':  [],
        }
        for token, gold_pos in sent['tokens']:
            pred_pos = predict_pos(token, sent['text'])
            all_gold.append(gold_pos)
            all_pred.append(pred_pos)
            sent_result['tokens'].append({
                'token':   token,
                'gold':    gold_pos,
                'pred':    pred_pos,
                'correct': pred_pos == gold_pos,
            })
        results.append(sent_result)

    total   = len(all_gold)
    correct = sum(g == p for g, p in zip(all_gold, all_pred))
    accuracy = correct / total if total else 0.0

    # Per-class P / R / F1
    labels = sorted(set(all_gold) | set(all_pred))
    class_metrics = {}
    for lbl in labels:
        tp = sum(g == lbl and p == lbl for g, p in zip(all_gold, all_pred))
        fp = sum(g != lbl and p == lbl for g, p in zip(all_gold, all_pred))
        fn = sum(g == lbl and p != lbl for g, p in zip(all_gold, all_pred))
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec  = tp / (tp + fn) if (tp + fn) else 0.0
        f1   = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
        class_metrics[lbl] = {
            'precision': prec,
            'recall':    rec,
            'f1':        f1,
            'support':   sum(g == lbl for g in all_gold),
        }

    macro_f1    = (sum(m['f1'] for m in class_metrics.values())
                   / len(class_metrics) if class_metrics else 0.0)
    weighted_f1 = (sum(m['f1'] * m['support'] for m in class_metrics.values())
                   / total if total else 0.0)

    return {
        'accuracy':     accuracy,
        'macro_f1':     macro_f1,
        'weighted_f1':  weighted_f1,
        'class_metrics': class_metrics,
        'total':        total,
        'correct':      correct,
        'results':      results,
        'gold':         all_gold,
        'pred':         all_pred,
    }


def print_report(ev):
    """Pretty-print evaluation report to stdout."""
    print('\n' + '=' * 62)
    print(' RULE-BASED POS TAGGER  —  EVALUATION RESULTS')
    print('=' * 62)
    print(f"\n  Overall Accuracy : {ev['accuracy']:.4f}  "
          f"({ev['correct']}/{ev['total']} correct)")
    print(f"  Macro  F1        : {ev['macro_f1']:.4f}")
    print(f"  Weighted F1      : {ev['weighted_f1']:.4f}")

    print(f"\n  {'Label':<10} {'Precision':>10} {'Recall':>10} "
          f"{'F1':>10} {'Support':>10}")
    print('  ' + '-' * 50)
    for lbl in sorted(ev['class_metrics']):
        m = ev['class_metrics'][lbl]
        print(f"  {lbl:<10} {m['precision']:>10.4f} {m['recall']:>10.4f} "
              f"{m['f1']:>10.4f} {m['support']:>10}")

    # Errors
    errors = [
        t for s in ev['results'] for t in s['tokens'] if not t['correct']
    ]
    if errors:
        print(f"\n{'=' * 62}")
        print(f' ERRORS  ({len(errors)} total)')
        print('=' * 62)
        confusion = Counter((e['gold'], e['pred']) for e in errors)
        print('\n  Top confusion pairs  (gold → pred):')
        for (gold, pred), cnt in confusion.most_common(10):
            print(f'    {gold:<8} → {pred:<8}  ×{cnt}')
        print('\n  Error details:')
        for e in errors:
            sent = next(s for s in ev['results']
                        if any(t is e for t in s['tokens']))
            ctx = sent['text'][:70] + ('…' if len(sent['text']) > 70 else '')
            print(f"    [{sent['sent_id']}] '{e['token']}'  "
                  f"gold={e['gold']}  pred={e['pred']}")
            print(f"           {ctx}")
    else:
        print('\n  No errors — perfect score on this split.')

    print()


# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='Rule-based POS tagger for Cantonese-English code-switching')
    parser.add_argument('--input',   required=True,
                        help='Input CoNLL file (e.g. ../../data/test.conll)')
    parser.add_argument('--output',  default=None,
                        help='Optional output CoNLL file for predictions')
    args = parser.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        sys.exit(f'Error: file not found — {args.input}')

    print(f'Reading  : {in_path}')
    sentences = read_conll(str(in_path))
    print(f'Loaded   : {len(sentences)} sentences')

    ev = evaluate(sentences)
    print_report(ev)

    # ── Save metrics JSON ────────────────────────────────────────
    metrics_dir = Path(__file__).parent / 'results'
    metrics_dir.mkdir(parents=True, exist_ok=True)
    metrics_path = metrics_dir / f'{in_path.stem}_metrics.json'
    with open(metrics_path, 'w', encoding='utf-8') as fh:
        json.dump({
            'input_file':    str(in_path),
            'total_tokens':  ev['total'],
            'correct':       ev['correct'],
            'accuracy':      ev['accuracy'],
            'macro_f1':      ev['macro_f1'],
            'weighted_f1':   ev['weighted_f1'],
            'class_metrics': ev['class_metrics'],
        }, fh, indent=2, ensure_ascii=False)
    print(f'Metrics saved : {metrics_path}')

    # ── Optionally write prediction CoNLL ────────────────────────
    if args.output:
        write_conll(ev['results'], args.output)
        print(f'Predictions   : {args.output}')


if __name__ == '__main__':
    main()
