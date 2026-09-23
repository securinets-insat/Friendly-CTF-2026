# #40 "Onions" — Walkthrough (INTERNAL)

**Category:** Encoding · **Tier:** 🟢 Easy · **Artifact(s):** `message.txt`
**Flag:** `Securinets{p33l_th3_3nc0d1ng_l4y3rs}`

---

## What it teaches

| Skill | Why it matters |
|---|---|
| Recognising layered encodings | base64 vs hex vs ROT13 by eye, and unwrapping in order. |

---

## Intended path

### 1. Look at it
`message.txt` holds one long token ending in `=` — base64.

### 2. Peel the layers, outermost first
```
base64 -d       -> a hex string (only 0-9a-f)
xxd -r -p       -> ROT13 text
```
Then undo ROT13 (`tr 'A-Za-z' 'N-ZA-Mn-za-m'`) to get the flag.

### 3. Or use CyberChef
Drop it in and hit *Magic* — it detects base64 -> hex -> ROT13.

---

## Hint ladder

1. **The trailing `=` is a giveaway for one common encoding.**
2. **It's base64, and what comes out is hex, and what comes out of THAT is rotated.**
3. **base64 -> from-hex -> ROT13. CyberChef Magic does it in one shot.**

---

## Build provenance
flag -> ROT13 -> hex -> base64, written to `message.txt`. Round-trip verified.
