# #15 "Off The Record" — Walkthrough (INTERNAL)

**Category:** Forensics · **Tier:** 🟢🟡 Easy–Medium
**Artifact:** `voicemail.wav` (1.0 MB, ~11.6 s, mono 44.1 kHz)
**Flag:** `Securinets{SP3CTR0_4ND_DTMF_7318}`

Two channels, both required:
- **Spectrogram** (1–6 s) spells `SP3CTR0_4ND_DTMF_`
- **DTMF tones** (~6.5–7.5 s) decode to `7318`
- **Reversed speech** (~8.5–11.6 s) is an audible red herring

---

## What it teaches

**One audio file can carry information in several independent domains, and finding one is
not finishing.** A player must inspect the *visual* (spectrogram) and *tonal* (DTMF)
representations, not just listen.

| Skill | Why it matters outside the CTF |
|---|---|
| Reading a spectrogram (Audacity / Sonic Visualiser / `sox -n spectrogram`) | The single most useful audio-forensics view |
| Recognising DTMF and decoding it (`multimon-ng -a DTMF`) | Real telephony/keypad capture analysis |
| Recognising reversed speech | Common audio-stego and prank technique |
| Not stopping at the first hit | The whole point — the flag needs two of the three channels |

---

## Intended path

### 1. Listen, then look

Played back, the file is mostly harsh tones and, at the end, garbled speech. Listening
alone yields nothing usable — the cue to switch to a **spectrogram**.

### 2. Spectrogram → the text half

Audacity (Spectrogram track view), Sonic Visualiser, or:

```
sox voicemail.wav -n spectrogram -o out.png
```

The 1–6 s region plainly renders, in the 0.6–3.6 kHz band:

```
SP3CTR0_4ND_DTMF_
```

Underscores are rendered literally (low horizontal bars), and the **trailing underscore**
signals that the string continues — the flag isn't complete yet.

### 3. The tone burst → DTMF

Right after the text (~6.5–7.5 s) are four two-tone bursts — the classic DTMF look (one low +
one high band each). Decode:

```
sox voicemail.wav -t raw -r 22050 -e signed -b 16 -c 1 - | multimon-ng -a DTMF -t raw -
```

```
DTMF: 7
DTMF: 3
DTMF: 1
DTMF: 8
```

→ `7318`. (multimon-ng needs raw/`sox` piping — it only takes WAV directly on some builds.)

### 4. Assemble

Spectrogram text + DTMF digits, joined on the trailing underscore:

```
Securinets{SP3CTR0_4ND_DTMF_7318}
```

What you see is what you type — uppercase, underscores as shown, no guessing about
case/separators.

---

## The red herring

The last ~3 s (8.5–11.6 s) is **reversed speech**. A curious player will reverse it:

```
sox voicemail.wav out.wav reverse      # then play out.wav
```

…and hear: *"there is nothing to hear on this channel, keep looking elsewhere."* It is
audible, it is obviously deliberate, and it says explicitly that it's a dead end — a fair
troll that rewards the reversing instinct with a wink, not a punishment. It also looks
"interesting" in the spectrogram (speech formants) to pull attention away from the DTMF
bursts.

---

## Alternative paths that legitimately work

- Sonic Visualiser instead of Audacity/sox for the spectrogram — same text.
- Decoding DTMF by ear or by hand from the two-tone frequencies (`697/770/852/941` ×
  `1209/1336/1477`) — slow but valid.
- Feeding the whole file to `multimon-ng` with several demods enabled — DTMF still surfaces;
  the reversed speech produces nothing.

No brute force; both halves are directly recoverable.

---

## Hint ladder

1. **"Don't just listen — *look*. What does a spectrogram show you?"**
2. **"You found text ending in an underscore. Something completes it. Those sharp two-tone
   beeps have a name — and a decoder."**
3. **"`multimon-ng -a DTMF` on the beeps → four digits. Append them to the spectrogram text.
   (The garbled voice at the end is a decoy — reverse it if you want a laugh.)"**

---

## Failure modes

| Symptom | Cause / fix |
|---|---|
| Player submits `Securinets{SP3CTR0_4ND_DTMF_}` | Stopped at the spectrogram. Hint 2 — the trailing `_` means more follows. |
| Player submits just `7318` | Found DTMF, missed the spectrogram. Hint 1. |
| Wrong case / spaces vs underscores | Shouldn't happen — spectrogram renders the literal string. If it does, the platform flag check can be made case-insensitive as a safety net. |
| `multimon-ng` prints nothing | They fed it WAV directly on a build that needs raw. Pipe via `sox … -t raw … -`. |
| Player chases the reversed voice | Red herring working as designed; it tells them so. |

---

## Build provenance

- Build tree: `build/ch15/` — `text.txt`, `spectro.wav`, `dtmf.wav`, `herring*.wav`,
  `sil.wav`, `voicemail_raw.wav`, `spectro_check.png`; **none shipped**. `dist/` holds only
  `voicemail.wav`, `README.md`, `SHA256SUMS`.
- Spectrogram text: `figlet -f banner "SP3CTR0_4ND_DTMF_"` → pixel grid → additive
  sine synthesis (pure-Python `wave`), each glyph row mapped to a frequency in 0.6–3.6 kHz,
  0.045 s per column.
- DTMF: standard low/high tone pairs for `7318`, 0.18 s tone + 0.10 s gap, synthesized in
  Python.
- Red herring: `espeak-ng` TTS of the troll line → `sox … reverse`.
- Assembled with `sox` (concatenation + 0.4 s silences), resampled to 44.1 kHz, `gain -n -3`.
- Verified on the **final** file: DTMF decodes to 7318; spectrogram text legible at default
  zoom; no plaintext flag in the WAV bytes.

**Difficulty dial:** to make it harder, narrow the spectrogram frequency band and lower its
amplitude so it's faint at default zoom (forces contrast adjustment), or hide the DTMF under
low-level noise. Kept clear here for Easy–Medium.
