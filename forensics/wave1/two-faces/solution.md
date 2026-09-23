# #52 "Two Faces" — Walkthrough (INTERNAL)

**Category:** Polyglot · **Tier:** 🟢 Easy · **Artifact(s):** `capture.png`
**Flag:** `Securinets{0n3_f1l3_tw0_f0rm4ts}`

---

## What it teaches

| Skill | Why it matters |
|---|---|
| File-in-file / polyglot thinking | One file can carry a second complete file; both halves are needed. |

---

## Intended path

### 1. Open as an image
`capture.png` is a valid PNG (`file` confirms) and draws the first half: `Securinets{0n3_f1l3_`.

### 2. Find the second face
`binwalk capture.png` shows a PDF embedded after the image data. Carve it:
```
binwalk -e capture.png     # or:
# find %PDF .. %%EOF and dd it out
```

### 3. Read the PDF
`pdftotext` the carved PDF -> `second half: tw0_f0rm4ts}`. Concatenate the two halves for the full flag.

## Why grep/eyeball doesn't shortcut it
Half the flag is PNG pixels, half is PDF text — neither alone is complete.

---

## Hint ladder

1. **`file` says PNG, but is that all it is? Run `binwalk`.**
2. **A full PDF is appended after the PNG. Carve it out.**
3. **PNG pixels give the first half; the embedded PDF gives the second — join them.**

---

## Build provenance
Valid PNG (first half drawn in pixels) with a complete hand-built PDF (second half as text) appended after IEND. `file` reports PNG; binwalk/foremost carve the PDF.
