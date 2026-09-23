# #46 "Cut Short" — Walkthrough (INTERNAL)

**Category:** Stego / File structure · **Tier:** 🟢 Easy · **Artifact(s):** `diagnostic.png`
**Flag:** `Securinets{r41s3_th3_1hdr_h31ght}`

---

## What it teaches

| Skill | Why it matters |
|---|---|
| PNG IHDR structure | The declared height can lie; the pixel data for the hidden rows is still present. |

---

## Intended path

### 1. Notice the crop
The image ends abruptly. The real content is taller than the header claims.

### 2. Edit the IHDR height
Height is a big-endian uint32 at file offset 20 (sig 8 + len 4 + 'IHDR' 4 + width 4). It currently reads 150. Raise it to the true 300 and fix the IHDR CRC (next 4 bytes = CRC32 of `IHDR`+13 data bytes). `pngcheck -v` helps; tools like `pcrt.py` automate it.

### 3. Read the flag
With full height, the bottom rows render and the flag appears.

## Why grep/eyeball doesn't shortcut it
The IDAT holds all 300 scanlines; the header just under-reports the height so viewers stop early.

---

## Hint ladder

1. **The image looks cut off. Where is a PNG's height stored?**
2. **IHDR height (offset 20, big-endian uint32) is smaller than the real data.**
3. **Set height to 300 and recompute the IHDR CRC; the flag is in the recovered rows.**

---

## Build provenance
Real height 300; IHDR height rewritten to 150 with a corrected IHDR CRC so it opens without error but hides the bottom. IDAT unchanged.
