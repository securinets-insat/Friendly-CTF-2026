# #45 "Too Dark" — Walkthrough (INTERNAL)

**Category:** Stego · **Tier:** 🟢 Easy · **Artifact(s):** `midnight.png`
**Flag:** `Securinets{bl4ck_0n_bl4ck_r3v34l3d}`

---

## What it teaches

| Skill | Why it matters |
|---|---|
| Low-contrast stego | Flag hidden as near-black pixels; revealed by adjusting levels. |

---

## Intended path

### 1. It's not empty
`midnight.png` looks black but isn't — the flag is drawn in `#010101` on `#000000`.

### 2. Stretch the contrast
GIMP Colors -> Levels (pull the white point down), or `convert midnight.png -level 0%,1% out.png`, or open in Stegsolve and browse bit planes.

### 3. Read the flag
The text pops out.

## Why grep/eyeball doesn't shortcut it
`strings`/`grep` find nothing — the flag is pixels one shade off black.

---

## Hint ladder

1. **Is it REALLY pure black? Check the pixel values.**
2. **The flag is drawn one step above black. Boost the contrast / levels.**
3. **`convert midnight.png -level 0%,1% out.png` then open out.png.**

---

## Build provenance
Flag drawn at RGB (1,1,1) on (0,0,0). Verified max pixel value <=2 and a few hundred ink pixels.
