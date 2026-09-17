#!/usr/bin/env python3
import socket
import sys

from attachments.detector import Detector, PRINTABLE


def solve():
    detector = Detector()
    words = []

    for branch in detector.branches:
        for channel, head in zip(branch["weight"], branch["head"]):
            if head >= 0:
                continue
            word = bytes(
                max(
                    PRINTABLE,
                    key=lambda char: sum(
                        a * b for a, b in zip(detector.embedding[char], weights)
                    ),
                )
                for weights in channel
            )
            if b"*/" not in word and word not in words:
                words.append(word)

    payload = b""
    score = detector.score(payload)

    while score >= detector.threshold:
        best = None
        for word in words:
            for separator in ((b"",) if not payload else (b" ", b"_", b"~", b"|")):
                extra = separator + word
                trial = payload + extra
                if len(trial) > detector.max_note or b"*/" in trial:
                    continue
                new_score = detector.score(trial)
                gain = score - new_score
                if gain <= 0:
                    continue
                key = (gain / len(extra), gain)
                if best is None or key > best[0]:
                    best = (key, word, trial, new_score)
        if best is None:
            raise RuntimeError("no payload found")
        _, word, payload, score = best
        words.remove(word)

    return detector, payload


def send(host, port, payload):
    with socket.create_connection((host, port)) as sock:
        data = b""
        while b"note> " not in data:
            data += sock.recv(4096)
        sock.sendall(payload + b"\n")
        while True:
            block = sock.recv(4096)
            if not block:
                break
            sys.stdout.buffer.write(block)


def main():
    detector, payload = solve()
    print(payload.decode(), flush=True)
    print(
        f"{len(payload)}/{detector.max_note} bytes, logit {detector.score(payload):.4f}",
        flush=True,
    )

    if len(sys.argv) == 3:
        send(sys.argv[1], int(sys.argv[2]), payload)
    elif len(sys.argv) != 1:
        raise SystemExit(f"usage: {sys.argv[0]} [host port]")


if __name__ == "__main__":
    main()
