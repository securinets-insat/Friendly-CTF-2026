# #50 "Morse Beeps" — Walkthrough (INTERNAL)

**Category:** Audio · **Tier:** 🟢 Easy · **Artifact(s):** `transmission.wav`
**Flag:** `Securinets{D0TD4SHM0RS3C0D3}`

---

## What it teaches

| Skill | Why it matters |
|---|---|
| Decoding Morse from audio | Recognising and reading Morse by ear or with a decoder. |

---

## Intended path

### 1. Listen / look
Open in Audacity — clear short and long tones with gaps: Morse code.

### 2. Decode
Feed it to an online Morse-audio decoder, or read it by hand (dot = short, dash = long, letter gaps between). It spells `D0TD4SHM0RS3C0D3`.

### 3. Wrap it
Wrap the decoded text: `Securinets{D0TD4SHM0RS3C0D3}`.

## Why grep/eyeball doesn't shortcut it
Only A-Z and 0-9 are in the Morse; the braces and prefix you add yourself.

---

## Hint ladder

1. **Short and long beeps with gaps — what encoding is that?**
2. **It's Morse. Decode short=dot, long=dash.**
3. **Decoded text is `D0TD4SHM0RS3C0D3`; wrap in Securinets{ }.**

---

## Build provenance
Pure-Python WAV: 650 Hz tones at 15 WPM, standard dot/dash and 1/3-unit gaps, with click fades. Envelope-decoded back to the exact string during verification.
