# #36 "Bad Magic" — Walkthrough (INTERNAL)

**Category:** File repair · **Tier:** 🟢 Easy · **Artifact(s):** `photo.png`
**Flag:** `Securinets{f1x_th3_m4g1c_by73s}`

---

## What it teaches

| Skill | Why it matters |
|---|---|
| File signatures (magic bytes) | Every format has a fixed header; a broken one is the most common 'corrupt file' cause and the easiest to repair. |

---

## Intended path

### 1. See the damage
`xxd photo.png | head -1` shows the file starts with `00 00 00 00` instead of the PNG signature. `file` says `data`.

### 2. Restore the signature
A PNG must start with `89 50 4E 47 0D 0A 1A 0A`. Fix the first 8 bytes in any hex editor (`xxd`, `hexedit`, `010`, `ghex`):
```
printf '\x89PNG\r\n\x1a\n' | dd of=photo.png bs=1 conv=notrunc
```

### 3. Open it
The PNG now opens and draws the flag.

## Why grep/eyeball doesn't shortcut it
Only the first 8 bytes are wrong; the rest of the file (IHDR, IDAT, IEND) is intact.

---

## Hint ladder

1. **What are the first bytes of a healthy PNG? Compare against this file.**
2. **The 8-byte PNG signature was zeroed.**
3. **Write back `89 50 4E 47 0D 0A 1A 0A` at offset 0, then open it.**

---

## Build provenance
Valid flag PNG with its 8-byte signature zeroed. IHDR/IDAT/IEND untouched, so restoring the signature fully repairs it.
