# #10 "Dead Drop" — Walkthrough (INTERNAL)

**Category:** Forensics · **Tier:** 🟢🟡 Easy–Medium
**Artifacts:** `market.png` (221 KB) + `harbor.jpg` (18 KB)
**Flag:** `Securinets{tw0_st3g0s_0n3_ch41n}`
**Passphrase (bridge secret):** `tr4d3_w1nds_2019` — LSB-hidden in the PNG, feeds steghide on the JPG

---

## What it teaches

**A stego chain: one carrier hides the key to the next.** Two images, two *different*
techniques, and the output of the first is the input to the second. It also teaches that
**file format dictates tool** — `zsteg` reads PNG/BMP, `steghide` takes JPEG/BMP/WAV — so
the formats themselves tell you which tool to point where.

| Skill | Why it matters outside the CTF |
|---|---|
| LSB extraction with `zsteg` on lossless images | The first thing you run on any suspect PNG/BMP |
| Reading zsteg's channel notation (`b1,rgb,lsb,xy`) | Distinguishing a real payload from bit-plane noise |
| `steghide` extract with a passphrase | The most common password-protected image stego |
| Matching technique to format | Stops players running the wrong tool on the wrong file |
| Not stopping at the first find | The chain punishes tunnel vision |

---

## Intended path

### 1. Triage both images

```
file market.png harbor.jpg
```

A PNG and a JPEG. Format matters: PNG is lossless (LSB stego survives, `zsteg` applies),
JPEG is lossy (LSB is destroyed by compression, so `steghide`'s DCT-domain embedding is the
relevant technique). An experienced player already suspects zsteg→PNG, steghide→JPG.

### 2. LSB on the PNG

```
zsteg market.png
```

```
b1,rgb,lsb,xy       .. text: "tr4d3_w1nds_2019"
```

Plain `zsteg` (no `-a` needed) surfaces it on the standard `b1,rgb,lsb,xy` channel — bit
plane 1, RGB channel order, LSB, row-major pixel scan. That is exactly how the passphrase
was embedded. `zsteg -a` shows it too, buried among noise from the other bit planes.

This looks like a passphrase, not a flag. The player has to realise it's a **key for
something else**.

### 3. The format steers you to the JPG

The natural next move — `steghide extract -sf market.png` — fails loudly:

```
steghide: the file format of the file "market.png" is not supported.
```

steghide doesn't do PNG. The only other file is `harbor.jpg`, which steghide *does* accept.
That failure is a guide rail, not a dead end.

### 4. steghide on the JPG with the recovered passphrase

```
steghide extract -sf harbor.jpg -p tr4d3_w1nds_2019
```

```
wrote extracted data to "secret.txt".
```

```
cat secret.txt
```

```
Meet at the usual place. Bring the manifest.
Securinets{tw0_st3g0s_0n3_ch41n}
```

---

## The red herring

`harbor.jpg` carries EXIF:

```
GPS Latitude  : 36 deg 51' 10" N
GPS Longitude : 10 deg 19' 24" E     (Carthage ruins, Tunis)
Camera Model  : Canon EOS 200D
Date/Time     : 2019:06:14 17:42:08
Artist        : pulgaa
```

`exiftool harbor.jpg` is the *first* thing many players run on a JPEG, so they find the GPS
immediately. It points at a real landmark and leads nowhere — a plausible time sink that
rewards the habit of "check EXIF first" with a dead end, teaching that metadata is not the
same as payload. The camera/date fields also make the photo read as a genuine 2019 holiday
snap rather than a synthetic file.

The other zsteg bit-plane lines (`b2,*`, `b3,*` noise like `"z,''''''"`) are incidental
distractors — real LSB-analysis clutter that a player must learn to see past to find the one
clean `b1,rgb,lsb,xy` line.

---

## Alternative paths that legitimately work

- `zsteg -a market.png` (exhaustive) instead of the default scan — same result, more noise.
- `stegsolve` / manual bit-plane inspection to read the LSB text visually. Valid, slower.
- Running `steghide extract` on `harbor.jpg` with a **wrong** guess first — it fails
  cleanly (`could not extract any data with that passphrase`), which confirms the passphrase
  must come from elsewhere. Good failure feedback, not a trap.

No brute force needed: the passphrase is handed over by the first stage.

---

## Hint ladder

1. **"Two images, two formats. Which stego tool works on a PNG, and which works on a JPEG?
   They are not the same tool."**
2. **"`zsteg` the PNG. What it gives you is not the flag — it's a password. For what?"**
3. **"`steghide extract -sf harbor.jpg -p <the string from zsteg>`."**

---

## Failure modes

| Symptom | Cause / fix |
|---|---|
| Player runs `steghide` on the PNG and gives up | Expected friction — steghide rejects PNG. Hint 1. |
| Player submits `tr4d3_w1nds_2019` as the flag | They stopped at stage 1. It's a passphrase; the flag is in the JPG. |
| Player chases the GPS coordinates | Red herring working as designed. |
| `zsteg` shows only noise | They ran it on `harbor.jpg` (JPEG — LSB is meaningless there). Run it on the PNG. |
| steghide "could not extract" with the right pass (authors) | An EXIF edit that recompresses the JPEG would corrupt the DCT payload. We used `exiftool` (APP1 only, no recompress) and re-verified extraction — safe. |

---

## Build provenance

- Build tree: `build/ch10/` — `secret.txt`, `harbor_clean.jpg`, `harbor.ppm`, `verify.txt`,
  `out.txt`; **none shipped**. `dist/10-dead-drop/` holds only `market.png`, `harbor.jpg`,
  `README.md`, `SHA256SUMS`.
- `market.png`: 480×320 RGB carrier generated with pure-Python zlib; passphrase embedded by
  setting the LSB of consecutive R,G,B bytes in row-major order (MSB-first per byte), which
  is precisely zsteg's `b1,rgb,lsb,xy` scan. Verified recoverable from the *shipped* file.
- `harbor.jpg`: PPM cover generated in Python → `cjpeg -quality 88` (installed
  `libjpeg-turbo-progs`; no ImageMagick/PIL on the box) → `steghide embed` with the
  passphrase → `exiftool` GPS red herring added last.
- Leak-checked: flag absent from both carriers' plaintext, passphrase not plaintext in the
  JPG.

**Difficulty dial:** to make it harder, embed the passphrase on a non-default zsteg channel
(e.g. `b1,bgr,lsb` or a higher bit plane) so plain `zsteg` misses it and the player must run
`zsteg -a` and reason about which line is signal. Kept on the default channel here so
Easy–Medium stays Easy–Medium.
