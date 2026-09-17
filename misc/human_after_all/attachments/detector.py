#!/usr/bin/env python3
import argparse
import json
import math
from pathlib import Path


ROOT = Path(__file__).parent
PRINTABLE = range(32, 127)


class BadNote(ValueError):
    pass


class Detector:
    def __init__(self, weights=None, source=None):
        weights = Path(weights or ROOT / "detector_weights.json")
        source = Path(source or ROOT / "Submission.java")
        model = json.loads(weights.read_text())

        self.embedding = model["embedding"]
        self.branches = model["branches"]
        self.bias = model["output_bias"]
        self.threshold = model["threshold"]
        self.max_note = model["max_note"]
        self.marker = model["marker"].encode()
        self.template = source.read_bytes()

        if self.template.count(self.marker) != 1:
            raise ValueError("bad source template")
        self._make_tables()

    def _make_tables(self):
        for branch in self.branches:
            tables = []
            for channel in branch["weight"]:
                table = []
                for weights in channel:
                    table.append(
                        [
                            sum(a * b for a, b in zip(row, weights))
                            for row in self.embedding
                        ]
                    )
                tables.append(table)
            branch["table"] = tables

    def clean(self, note):
        if isinstance(note, str):
            try:
                note = note.encode("ascii")
            except UnicodeEncodeError:
                raise BadNote("ASCII only")
        if type(note) is not bytes:
            raise BadNote("expected bytes")
        if len(note) > self.max_note:
            raise BadNote("too long")
        if any(byte not in PRINTABLE for byte in note):
            raise BadNote("printable ASCII only")
        if b"*/" in note:
            raise BadNote("nice try")
        return note

    def render(self, note):
        return self.template.replace(self.marker, self.clean(note))

    def score(self, note):
        data = self.render(note)
        score = self.bias

        for branch in self.branches:
            width = branch["width"]
            for table, conv_bias, head in zip(
                branch["table"], branch["bias"], branch["head"]
            ):
                pooled = 0.0
                for start in range(len(data) - width + 1):
                    value = conv_bias
                    for offset in range(width):
                        value += table[offset][data[start + offset]]
                    pooled = max(pooled, value)
                score += head * pooled
        return score

    def classify(self, note):
        score = self.score(note)
        if score >= 0:
            probability = 1 / (1 + math.exp(-score))
        else:
            value = math.exp(score)
            probability = value / (1 + value)
        verdict = "AI" if score >= self.threshold else "HUMAN"
        return score, probability, verdict


def main():
    parser = argparse.ArgumentParser(description="Score a note in Submission.java")
    parser.add_argument("--note", default="")
    args = parser.parse_args()

    detector = Detector()
    try:
        note = detector.clean(args.note)
        score, probability, verdict = detector.classify(note)
    except BadNote as error:
        parser.error(str(error))

    print(f"Note bytes: {len(note)}/{detector.max_note}")
    print(f"AI logit: {score:.6f}")
    print(f"AI probability: {probability:.12f}")
    print(f"Verdict: {verdict}")


if __name__ == "__main__":
    main()
