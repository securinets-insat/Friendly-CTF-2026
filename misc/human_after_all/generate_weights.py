#!/usr/bin/env python3
import json
import math
from pathlib import Path
import random


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "attachments" / "detector_weights.json"
TEMPLATE = ROOT / "attachments" / "Submission.java"
SEED = 0x484154455253
EMBEDDING_SIZE = 24
FILTER_SCALE = 4.0
EXACT_ACTIVATION = 1.0
MAX_NOTE = 72
TARGET_BASE_LOGIT = 41.0


# (pattern, output weight)
FILTERS = {
    3: [
        ("pub", 2.8),
        ("sta", 2.4),
        ("int", 2.6),
        ("ret", 2.5),
        ("LOL", 5.5),
        ("BOT", 5.5),
        ("voi", -4.5),
        ("out", -4.2),
        ("tbh", -3.6),
        ("imo", -3.3),
        ("idk", -3.8),
        ("hmm", -3.5),
    ],
    5: [
        ("publi", 2.7),
        ("stati", 2.5),
        ("retur", 2.4),
        ("value", 2.6),
        ("ROBOT", 6.0),
        ("MODEL", 5.8),
        ("print", -4.2),
        ("class", -3.9),
        ("kinda", -4.0),
        ("maybe", -3.9),
        ("uhhhh", -4.1),
        ("typoo", -4.0),
    ],
    7: [
        ("public ", 2.8),
        ("static ", 2.7),
        ("return ", 2.5),
        ("String[", 2.6),
        ("AI_GEN!", 7.0),
        ("BOTCODE", 7.0),
        ("println", -4.3),
        ("private", -4.0),
        ("raw_typ", -4.8),
        ("ummm_ok", -4.6),
        ("xxBOTyy", -5.4),
        ("zzLOLzz", -5.2),
    ],
    11: [
        ("public fina", 2.8),
        ("static void", 2.7),
        ("System.out.", 2.8),
        ("return resu", 2.6),
        ("GENERATED!!", 7.4),
        ("AUTOCODE_AI", 7.2),
        ("private sta", -4.4),
        ("Submission ", -4.2),
        ("honest_typo", -5.2),
        ("wrote_it_me", -5.0),
        ("ROBOTmaybe?", -6.6),
        ("MODELuhhhh?", -6.5),
    ],
}


def unit_vector(rng, size):
    vector = [rng.gauss(0.0, 1.0) for _ in range(size)]
    norm = math.sqrt(sum(value * value for value in vector))
    return [value / norm for value in vector]


def rounded(value):
    return round(value, 8)


def make_model():
    rng = random.Random(SEED)
    embedding = [unit_vector(rng, EMBEDDING_SIZE) for _ in range(256)]
    embedding = [[rounded(value) for value in row] for row in embedding]

    branches = []
    for width, specs in FILTERS.items():
        branch_weights = []
        branch_biases = []
        branch_head = []

        for target, head_weight in specs:
            encoded = target.encode("ascii")
            if len(encoded) != width:
                raise ValueError(f"{target!r} does not have width {width}")

            channel = []
            for byte in encoded:
                channel.append(
                    [
                        rounded(FILTER_SCALE * value + rng.gauss(0.0, 0.012))
                        for value in embedding[byte]
                    ]
                )
            branch_weights.append(channel)
            branch_biases.append(rounded(-(FILTER_SCALE * width - EXACT_ACTIVATION)))
            branch_head.append(float(head_weight))

        branches.append(
            {
                "width": width,
                "weight": branch_weights,
                "bias": branch_biases,
                "head": branch_head,
            }
        )

    model = {
        "format": "human-after-all-byte-cnn-v1",
        "embedding": embedding,
        "branches": branches,
        "output_bias": 0.0,
        "threshold": 0.0,
        "max_note": MAX_NOTE,
        "marker": "{{NOTE}}",
    }

    base_source = TEMPLATE.read_bytes().replace(b"{{NOTE}}", b"")
    base_without_output_bias = score_bytes(model, base_source)
    model["output_bias"] = rounded(TARGET_BASE_LOGIT - base_without_output_bias)
    return model


def score_bytes(model, source):
    embedding = model["embedding"]
    result = float(model["output_bias"])

    for branch in model["branches"]:
        width = int(branch["width"])
        for weights, bias, head_weight in zip(
            branch["weight"], branch["bias"], branch["head"]
        ):
            best = 0.0
            for start in range(len(source) - width + 1):
                activation = float(bias)
                for offset, position_weights in enumerate(weights):
                    byte_embedding = embedding[source[start + offset]]
                    activation += sum(
                        a * b for a, b in zip(byte_embedding, position_weights)
                    )
                best = max(best, activation)
            result += float(head_weight) * best
    return result


def main():
    model = make_model()
    OUTPUT.write_text(
        json.dumps(model, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    base = TEMPLATE.read_bytes().replace(b"{{NOTE}}", b"")
    print(f"wrote {OUTPUT}")
    print(f"base logit: {score_bytes(model, base):.6f}")


if __name__ == "__main__":
    main()
