# #29 "Ghost in the GPU" — Walkthrough (INTERNAL)

**Category:** Forensics — entropy hunting + numeric encoding · **Tier:** 🟡🟠 Medium–Hard
**Artifact:** `vram_dump.bin` (32 MB raw VRAM capture)
**Flag:** `Securinets{fp16_t3ns0r_gh0st}` (drawn in an fp16 tensor)

---

## What it teaches
There is **nothing to carve** — no magic bytes, no container, just device memory. The skill is
recognizing a **numeric dtype from its raw byte pattern** and reasoning about **tensor layout**.
It's `strings`/`binwalk`-proof by construction.

| Skill | Why it matters |
|---|---|
| Entropy sweep to find planted data in noise | The whole file is CSPRNG noise; the signal is the *low*-entropy region |
| Recognizing IEEE-754 **half-precision** (fp16) from bytes | `0x3C00`/`0xBC00` = `+1.0`/`-1.0` — invisible unless you try fp16 |
| Tensor layout reasoning (NCHW, shape) | The metadata says `(1,3,512,512)`; the element count baits a wrong 2D reshape |

---

## Intended path

### 1. Nothing carves
`file vram_dump.bin` → `data`. `binwalk` yields only coincidental false-positives in the noise.
Accept that there's no container.

### 2. Entropy sweep
Slide a 1 KB window; almost everything is ~7.99 bits/byte (random). Two regions collapse:
```
0x00100000  1 KB      ent ≈ 1.6   <- metadata blob (ASCII)
0x00900000  1.5 MB    ent ≈ 1.1   <- the payload (only bytes 0x00 / 0x3C / 0xBC)
```

### 3. Read the metadata, recognize the dtype
The 1 KB blob is a runtime tensor header:
```json
{"framework":"onnxruntime-gpu","node":"decoder/conv_out/Tanh",
 "tensor_shape":[1,3,512,512],"dtype":"float16","layout":"NCHW", ...}
```
The 1.5 MB region hexdumps as `00 3c 00 3c ... 00 bc 00 bc` — little-endian half-words
`0x3C00` and `0xBC00`. Those are **fp16 `+1.0` and `-1.0`**. It's a normalized (Tanh-output)
activation **tensor**, not an image buffer.

### 4. Reshape and render
```python
import numpy as np; from PIL import Image
d = open("vram_dump.bin","rb").read()
t = np.frombuffer(d[0x900000:0x900000+1*3*512*512*2], np.float16).reshape(1,3,512,512)
plane = t[0,0]                                   # NCHW -> channel 0
Image.fromarray(np.where(plane<=-0.5,0,255).astype("uint8")).save("flag.png")
```
`-1.0` is the ink → the flag is drawn in a pixel font:
```
Securinets{fp16_t3ns0r_gh0st}
```

---

## Trick & red herring
- **Trick:** no tool opens this — there is no format, only device memory holding an fp16 tensor.
  You must *recognize* the dtype (`0x3C00`/`0xBC00`) and honour the `NCHW` layout from the metadata.
- **Red herring:** the element count `3·512·512 = 786432` also factors as **1024×768** (a real display
  resolution). Reshaping to `1024×768` renders the flag **tiled** — readable but obviously "not right",
  which costs time before you take the metadata's `(1,3,512,512)` at face value.

---

## Build notes
`build/ch29/make_ch29.py` (numpy + Pillow, no VM): 32 MB `os.urandom` noise; a 1 KB JSON metadata
blob at `0x100000`; an fp16 tensor at `0x900000` where the flag mask is `-1.0` (ink) on `+1.0`
(background), replicated across 3 NCHW channels. `build/ch29/solve_ch29.py` reproduces the intended
path (entropy sweep → metadata → fp16 reshape → render) and was verified to render the flag legibly;
the flag is **not** ASCII-greppable in the dump. Answer key (`make_ch29.py`, the rendered PNG) stays
in `build/ch29`, not shipped.
