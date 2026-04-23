import os

def read_conll(filename):
    sents = []
    with open(filename, "r", encoding="utf-8") as f:
        tokens, pos_tags = [], []
        for line in f:
            line = line.strip()
            if line.startswith("#"):
                continue
            if not line:
                if tokens:
                    sents.append({"tokens": tokens, "pos_tags": pos_tags})
                tokens, pos_tags = [], []
            else:
                parts = line.split()
                tokens.append(parts[0])
                pos_tags.append(parts[1])
        if tokens:
            sents.append({"tokens": tokens, "pos_tags": pos_tags})
    return sents
