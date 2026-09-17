#!/usr/bin/env python3

from pathlib import Path


flag = b"Securinets{w0w_4_wh0l3_p4r4gr4ph_0f_l1t3r4lly_n0th1ng}"
cover = (
    "He posted fourteen paragraphs, called everyone an NPC, cited a cropped "
    "screenshot, and announced that silence was proof he won the argument."
)

words = []
for byte in flag:
    bits = f"{byte:08b}"
    words.append("".join("\u200b" if bit == "0" else "\u200c" for bit in bits))

hidden = "\u2060".join(words)
size = (len(hidden) + len(cover) - 1) // len(cover)
chunks = [hidden[i:i + size] for i in range(0, len(hidden), size)]

message = "".join(
    char + (chunks[i] if i < len(chunks) else "")
    for i, char in enumerate(cover)
)

Path(__file__).with_name("message.txt").write_text(message + "\n", encoding="utf-8")
