# #35 "Wrong Coat" — Walkthrough (INTERNAL)

**Category:** File types · **Tier:** 🟢 Easy · **Artifact(s):** `notes.txt`
**Flag:** `Securinets{ext3ns10ns_dont_d3f1n3_typ3}`

---

## What it teaches

| Skill | Why it matters |
|---|---|
| File extensions do not decide type | Magic bytes do. Triage should always start with `file`. |

---

## Intended path

### 1. Ask `file`
`file notes.txt` -> `PNG image data, 1100 x 200`. The extension lied.

### 2. Rename and open
`cp notes.txt notes.png` (or just open it in an image viewer). The flag is drawn across the image.

## Why grep/eyeball doesn't shortcut it
`strings`/`grep` on the file find nothing — the flag is pixels, not text. You must view the image.

---

## Hint ladder

1. **The name says .txt but does it open like text?**
2. **Run `file` on it.**
3. **It's a PNG. Rename to .png and open it.**

---

## Build provenance
A flag-bearing PNG (Pillow, Consolas) written out under a `.txt` filename. Flag rendered as pixels so it is not greppable.
