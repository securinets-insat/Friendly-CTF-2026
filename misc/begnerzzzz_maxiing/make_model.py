#!/usr/bin/env python3

import json
import math
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "detector_weights.json"
SOLVE = ROOT / "Solve.java"
SEED = 0xBEEFBABE2026
SIZE = 18
SCALE = 4.0
MAX_NOTE = 96
MAX_SOURCE = 20000
BANK_SIZE = 64
ACTIVE_COUNT = 10
TARGET_LOGIT = 44.0

BASE = {
    3: [("pub", 2.6), ("sta", 2.3), ("new", 2.1), ("try", 2.0)],
    5: [("class", 3.0), ("throw", 2.7), ("while", 2.3), ("byte[", 2.6)],
    7: [("reflect", 3.2), ("Message", 3.0), ("public ", 2.8)],
}


def unit(rng):
    row = [rng.gauss(0, 1) for _ in range(SIZE)]
    norm = math.sqrt(sum(x * x for x in row))
    return [round(x / norm, 8) for x in row]


def channel(rng, embedding, target):
    weights = []
    for byte in target.encode():
        weights.append([
            round(SCALE * value + rng.gauss(0, 0.01), 8)
            for value in embedding[byte]
        ])
    return weights, round(-(SCALE * len(target) - 1.0), 8)


def raw_score(model, nonce, source):
    from detector import Detector

    OUTPUT.write_text(json.dumps(model, separators=(",", ":")) + "\n")
    return Detector().score(nonce, source)


def build():
    rng = random.Random(SEED)
    embedding = [unit(rng) for _ in range(256)]
    branches = []

    for width, specs in BASE.items():
        branch = {"width": width, "weight": [], "bias": [], "head": [],
                  "scope": [], "gate": []}
        for target, head in specs:
            weights, bias = channel(rng, embedding, target)
            branch["weight"].append(weights)
            branch["bias"].append(bias)
            branch["head"].append(head)
            branch["scope"].append("full")
            branch["gate"].append(-1)
        branches.append(branch)

    alphabet = "abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    used = set()
    bank = []
    while len(bank) < BANK_SIZE:
        word = "".join(rng.choice(alphabet) for _ in range(5))
        if word not in used:
            used.add(word)
            bank.append(word)

    branch = {"width": 5, "weight": [], "bias": [], "head": [],
              "scope": [], "gate": []}
    for slot, target in enumerate(bank):
        weights, bias = channel(rng, embedding, target)
        branch["weight"].append(weights)
        branch["bias"].append(bias)
        branch["head"].append(-8.25)
        branch["scope"].append("note")
        branch["gate"].append(slot)
    branches.append(branch)

    return {
        "format": "maxing-gated-byte-cnn-v1",
        "embedding": embedding,
        "branches": branches,
        "output_bias": 0.0,
        "threshold": 0.0,
        "max_note": MAX_NOTE,
        "max_source": MAX_SOURCE,
        "bank_size": BANK_SIZE,
        "active_count": ACTIVE_COUNT,
    }


def main():
    model = build()
    source = SOLVE.read_bytes().replace(b"{{NOTE}}", b"")
    nonce = "0123456789abcdef"
    score = raw_score(model, nonce, source)
    model["output_bias"] = round(TARGET_LOGIT - score, 8)
    OUTPUT.write_text(json.dumps(model, separators=(",", ":")) + "\n")
    print(f"wrote {OUTPUT}")
    print(f"blank exploit logit: {raw_score(model, nonce, source):.4f}")


if __name__ == "__main__":
    main()
