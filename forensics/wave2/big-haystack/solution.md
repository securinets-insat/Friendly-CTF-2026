# #39 "Big Haystack" — Walkthrough (INTERNAL)

**Category:** Misc / Linux · **Tier:** 🟢 Easy · **Artifact(s):** `haystack.zip`
**Flag:** `Securinets{gr3p_d4sh_r_f1nds_1t}`

---

## What it teaches

| Skill | Why it matters |
|---|---|
| Recursive search | `grep -r` across a large tree — the bread-and-butter of triage. |

---

## Intended path

### 1. Unpack
`unzip -q haystack.zip`

### 2. Search recursively
`grep -rn 'Securinets{' logs/` returns the single matching line (`operator note: ...`).

### 3. Read the flag
That one line is the flag.

---

## Hint ladder

1. **You are not opening 2000 files by hand.**
2. **`grep` has a recursive flag.**
3. **`grep -rn 'Securinets{' .`**

---

## Build provenance
2000 filler `.txt` files of random words in `logs/NN/NN/`; the flag inserted on one line of one file, chosen by a seeded RNG.
