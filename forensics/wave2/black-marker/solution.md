# #38 "Black Marker" — Walkthrough (INTERNAL)

**Category:** Document forensics · **Tier:** 🟢 Easy · **Artifact(s):** `memo.pdf`
**Flag:** `Securinets{r3d4ct10n_1s_n0t_d3l3t10n}`

---

## What it teaches

| Skill | Why it matters |
|---|---|
| Visual redaction is not deletion | A black box drawn over text leaves the text in the content stream — copy/paste or `pdftotext` recovers it. |

---

## Intended path

### 1. Open it
A black bar covers the 'Recovery key:' line.

### 2. Extract the text layer
`pdftotext memo.pdf -` (or select-all + copy in a viewer). The text under the bar is right there in the output.

### 3. Read the flag
The recovery key is the flag.

## Why grep/eyeball doesn't shortcut it
The rectangle is drawn *after* the text in the content stream, so it only hides the pixels — the characters are still selectable/extractable.

---

## Hint ladder

1. **Try selecting the text under the black bar and copying it.**
2. **The characters were never removed, only covered.**
3. **`pdftotext memo.pdf -` prints the hidden line.**

---

## Build provenance
Hand-built one-page PDF (Courier). Text object writes all lines including the flag; a filled black rectangle is drawn over the last line afterward. Text layer intact for extraction.
