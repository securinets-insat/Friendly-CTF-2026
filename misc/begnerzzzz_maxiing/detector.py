#!/usr/bin/env python3

import argparse
import hashlib
import json
import math
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PRINTABLE = range(32, 127)


class BadSource(ValueError):
    pass


class Detector:
    def __init__(self, weights=None):
        path = Path(weights or ROOT / "detector_weights.json")
        model = json.loads(path.read_text())

        self.embedding = model["embedding"]
        self.branches = model["branches"]
        self.bias = model["output_bias"]
        self.threshold = model["threshold"]
        self.max_source = model["max_source"]
        self.max_note = model["max_note"]
        self.bank_size = model["bank_size"]
        self.active_count = model["active_count"]
        self._make_tables()

    def _make_tables(self):
        for branch in self.branches:
            tables = []
            for channel in branch["weight"]:
                table = []
                for weights in channel:
                    table.append([
                        sum(a * b for a, b in zip(row, weights))
                        for row in self.embedding
                    ])
                tables.append(table)
            branch["table"] = tables

    def clean_nonce(self, nonce):
        if isinstance(nonce, bytes):
            nonce = nonce.decode("ascii", "strict")
        if not re.fullmatch(r"[0-9a-f]{16}", nonce or ""):
            raise BadSource("bad nonce")
        return nonce

    def clean_source(self, source):
        if isinstance(source, str):
            source = source.encode("ascii", "strict")
        if not isinstance(source, bytes):
            raise BadSource("expected bytes")
        if not 256 <= len(source) <= self.max_source:
            raise BadSource("bad source size")
        if any(byte not in PRINTABLE and byte not in b"\r\n\t" for byte in source):
            raise BadSource("source must be ASCII")

        match = re.search(rb"/\* maxing:([ -~]*) \*/\s*\Z", source)
        if not match:
            raise BadSource("missing final maxing note")
        note = match.group(1)
        if len(note) > self.max_note or b"*/" in note:
            raise BadSource("bad maxing note")
        return source, note

    def active(self, nonce):
        digest = hashlib.sha256(("maxing:" + nonce).encode()).digest()
        chosen = []
        counter = 0
        while len(chosen) < self.active_count:
            block = hashlib.sha256(digest + counter.to_bytes(2, "big")).digest()
            for byte in block:
                slot = byte % self.bank_size
                if slot not in chosen:
                    chosen.append(slot)
                    if len(chosen) == self.active_count:
                        break
            counter += 1
        return set(chosen)

    def score(self, nonce, source):
        nonce = self.clean_nonce(nonce)
        source, note = self.clean_source(source)
        active = self.active(nonce)
        full = nonce.encode() + b"\n" + source
        result = self.bias

        for branch in self.branches:
            width = branch["width"]
            for table, bias, head, scope, gate in zip(
                branch["table"], branch["bias"], branch["head"],
                branch["scope"], branch["gate"]
            ):
                if gate >= 0 and gate not in active:
                    continue
                data = note if scope == "note" else full
                pooled = 0.0
                for start in range(len(data) - width + 1):
                    value = bias
                    for offset in range(width):
                        value += table[offset][data[start + offset]]
                    pooled = max(pooled, value)
                result += head * pooled
        return result

    def classify(self, nonce, source):
        score = self.score(nonce, source)
        if score >= 0:
            probability = 1 / (1 + math.exp(-min(score, 700)))
        else:
            value = math.exp(max(score, -700))
            probability = value / (1 + value)
        return score, probability, "AI" if score >= self.threshold else "HUMAN"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("nonce")
    parser.add_argument("source", type=Path)
    args = parser.parse_args()

    detector = Detector()
    score, probability, verdict = detector.classify(
        args.nonce, args.source.read_bytes()
    )
    print(f"AI logit: {score:.6f}")
    print(f"AI probability: {probability:.12f}")
    print(f"Verdict: {verdict}")


if __name__ == "__main__":
    main()
