#!/usr/bin/env python3

from pathlib import Path
import sys

from attachments.detector import BadNote, Detector


def main():
    detector = Detector()

    print("HUMAN AFTER ALL")
    print("The detector rejected Submission.java.")
    print("Current verdict: AI")
    print()
    print("You control {{NOTE}} inside the final /* {{NOTE}} */ comment.")
    print(f"Submit at most {detector.max_note} printable ASCII bytes.")
    print('The sequence "*/" is not allowed.')
    print()
    print("note> ", end="", flush=True)

    try:
        note = sys.stdin.buffer.readline(detector.max_note + 2)
        if note.endswith(b"\n"):
            note = note[:-1]
        score, probability, verdict = detector.classify(note)
    except BadNote:
        print("Invalid note.")
        return

    print(f"AI probability: {probability:.12f}")
    print(f"Verdict: {verdict}")

    if verdict == "HUMAN":
        print((Path(__file__).parent / "flag.txt").read_text().strip())


if __name__ == "__main__":
    main()
