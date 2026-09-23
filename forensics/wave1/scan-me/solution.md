# #42 "Scan Me" — Walkthrough (INTERNAL)

**Category:** Misc · **Tier:** 🟢 Easy · **Artifact(s):** `scan_me.png`
**Flag:** `Securinets{qr_c0d3s_4r3_fr33_p01nts}`

---

## What it teaches

| Skill | Why it matters |
|---|---|
| QR decoding | And that inverting colours doesn't stop a determined reader. |

---

## Intended path

### 1. Try to scan
A phone camera may refuse the inverted code.

### 2. Invert and decode
Invert back to black-on-white and decode:
```
zbarimg scan_me.png            # may read it as-is
# or: convert scan_me.png -negate n.png && zbarimg n.png
```

### 3. Read the flag
The decoded QR text is the flag.

## Why grep/eyeball doesn't shortcut it
The flag is the QR payload, not drawn text — you must actually decode the code.

---

## Hint ladder

1. **It's a QR code. What do you scan it with?**
2. **The colours are inverted; flip them back (negate) if your reader struggles.**
3. **`zbarimg` (or any phone app) after negating gives the flag.**

---

## Build provenance
`segno` QR of the flag (error level M), scaled x8 with border 4, then colour-inverted. Verified by rebuilding the module matrix from the image and matching segno's.
