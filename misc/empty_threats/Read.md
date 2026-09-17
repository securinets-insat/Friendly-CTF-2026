# EMPTY THREATS

## Challenge

The player receives only `message.txt`. It looks like an ordinary sentence,
but its byte size is much larger than the visible text.

## Solution

Inspecting the file with `xxd`, `od`, a hex editor, or Python reveals three
repeating Unicode code points:

- `U+200B` (zero-width space) is `0`;
- `U+200C` (zero-width non-joiner) is `1`;
- `U+2060` (word joiner) separates bytes.

Remove every visible character, replace the two zero-width characters with
bits, split on the word joiner, and decode each eight-bit group as ASCII.

```bash
python3 solver.py
```

Output:

```text
Securinets{w0w_4_wh0l3_p4r4gr4ph_0f_l1t3r4lly_n0th1ng}
```

Run `python3 make.py` whenever the flag or cover text changes.
