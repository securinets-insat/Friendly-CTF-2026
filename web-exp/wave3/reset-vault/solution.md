# #32 "Reset Vault" — Walkthrough (INTERNAL)

**Category:** Web · **Tier:** 🟡 Medium
**Stack:** Node/Express + MongoDB (see `build/ch32-reset-vault/`)
**Flag:** `Securinets{...}` — **generated fresh on every container boot** (32 random hex
inside the wrapper), stored only in the admin's encrypted note. Example from a test
instance: `Securinets{fac2b67120e6a38344bd75092b9a9dca}`.
**Reference solvers:** `build/ch32-reset-vault/solver/solve.py` (full auto, both paths) and
`solver1.py` (manual: paste a candidate note `_id`, get the plaintext).

---

## What it teaches

**A structured identifier is not a source of randomness.** The whole app hangs off one
helper, `lib/tokenGen.js`, that seeds a PRNG with a MongoDB `ObjectId` and reuses it for
three security-sensitive values: session cookies, password-reset tokens, and per-note
AES-256 keys. An `ObjectId` is only 12 bytes and mostly predictable, so every one of those
"random" values is recoverable by an attacker who can observe a single `ObjectId` the server
produced.

| Skill | Why it matters outside the CTF |
|---|---|
| Decomposing a MongoDB `ObjectId` (timestamp / per-process random / counter) | Recognising a whole class of ID-guessing bugs |
| Spotting a non-crypto PRNG standing in for `crypto.randomBytes` | The real-world root cause here |
| Reimplementing `seedrandom` to reproduce server output | Turns "looks random" into "fully predictable" |
| Reasoning about an entropy budget (bounded brute-force) | Knowing when a search is feasible vs hopeless |

No SQL/NoSQL injection is involved. The lesson: **"it came out of a random-looking function"
says nothing about whether it's guessable.**

---

## Background: why a MongoDB ObjectId is not random

A 12-byte `ObjectId` (24 hex chars) is:

| Bytes | Field | Property |
|------:|-------|----------|
| 0–3 | Unix timestamp (seconds) | Known to ~the second (leaks in HTTP `Date`, `createdAt`, etc.) |
| 4–8 | Per-process "random" value | Generated **once at driver startup**, then **constant** for the whole server process |
| 9–11 | Counter | Starts at a random 24-bit value, **increments by 1** for every `ObjectId()` the process creates |

The killer property is bytes 4–8: they are the same for *every* `ObjectId` the running
server makes. So if the attacker can see **one** real `ObjectId`, they know those 5 bytes for
all the others. Only the timestamp (constrained to a known second) and the counter
(constrained to a small monotonic range) vary — a tiny search space.

## The bug (conceptual)

```js
// lib/tokenGen.js  — one helper, reused everywhere
function generate(seed, byteLength) {
  const rng = seedrandom(seed.toString());          // seed = an ObjectId's 24-hex string
  let out = '';
  for (let i = 0; i < byteLength * 2; i++) out += Math.floor(rng() * 16).toString(16);
  return out;                                        // deterministic given the seed
}
```

Used as:
- **Session cookie:** `generate(new ObjectId(), 16)` → 32-hex, stored in `sessions`, set as a
  cookie with `httpOnly:false` (readable in the browser).
- **Reset token:** `generate(new ObjectId(), 10)` → 20-hex, 45-second expiry.
- **Note AES-256 key:** `generate(note._id, 32)` → 64-hex — **the note's own `_id` is the key
  seed**, and that `_id` is stored right next to the ciphertext.

`require("seedrandom")` defaults to the ARC4-based generator (not `alea`). The solver ports
that exact algorithm to Python so it reproduces the server's output byte-for-byte.

---

## The leak vector

`GET /notes` returns the logged-in user's own notes **including their `_id`s**. So any player
can, from their own account, read a genuine `ObjectId` minted by the server process. Decoding
it hands over the fixed random bytes (4–8) plus a live (timestamp, counter) anchor. That is
all the calibration needed to predict other `ObjectId`s — and therefore other tokens/keys.

---

## Intended path

Two routes reach the flag from the same insight. Both start with the same calibration.

### 0. Calibrate off your own account

```
register → login → POST /notes (create any note) → GET /notes
```

Read your note's `_id`, e.g. `6a9b45b404e4878d0ec37b9f`, and split it:

```
6a9b45b4  04e4878d0e  0ec37b9f
--------  ----------  --------
timestamp  random(5)   counter      ← random(5) is fixed for the whole server process
```

### Path A — predict the admin's reset token (account takeover)

1. `POST /forgot-password {username:"admin"}`. The server makes `seed = new ObjectId()` and
   stores `generate(seed,10)` with a **45-second** expiry. The HTTP `Date` response header
   gives the server's timestamp to the second.
2. Reconstruct that `seed`: timestamp = `Date` header (±1–2 s for rounding), random bytes =
   the ones you leaked, counter = a small window around your own note's counter (the reset
   `ObjectId` was created moments after yours, so its counter is close).
3. For each candidate `ObjectId`, compute `generate(candidate,10)` locally and POST it to
   `/reset-password` for `admin` — **within the 45-second window**, so it must be scripted.
4. One candidate matches → admin password is reset → log in as admin → read the flag note
   (the server decrypts owned notes on `GET /notes`).

`solve.py --method a` does exactly this; in testing it lands in well under a second.

### Path B — decrypt the flag note directly (no login, no reset)

1. The flag lives in an **encrypted** note owned by `admin`, created at server boot. Encrypted
   notes are readable by **anyone** via `GET /notes/:id` (it returns `ciphertext/iv/authTag`
   with no auth — the app's flawed reasoning being "it's already encrypted").
2. Guess the flag note's `_id`: it was one of the first `ObjectId`s the process created, so
   its counter is low and its timestamp ≈ container start; random bytes are the ones you know.
   Sweep that (timestamp × counter) space against `GET /notes/:id` until a real encrypted note
   comes back.
3. That note's `_id` **is** its AES key seed: `key = generate(_id, 32)`. Derive it locally and
   AES-256-GCM-decrypt the returned ciphertext → flag. No admin session ever touched.

`solve.py --method b` (or `solver1.py <id>` for the manual last step) does this.

```bash
cd build/ch32-reset-vault
pip install requests cryptography
python solver/solve.py --url http://TARGET:3000 --method both
```

---

## Why the two pieces matter together

- **AES-256-GCM itself is not broken** — the cipher is correct. The break is one level up: the
  key is a deterministic function of a guessable 12-byte value that sits in plain sight next to
  the ciphertext.
- **The `httpOnly:false` session cookie** is the self-referential tell that nudges players to
  realise these tokens all come from one weak generator, before they even look at `/notes`.
- **The 45-second reset expiry** is what forces Path A to be automated end-to-end rather than
  hand-run with curl.

## Difficulty / anti-frustration notes

- The `Date` header (or a note's `createdAt`) is the intended timestamp oracle — no need for
  timing side-channels.
- Counter search is bounded: the reset/flag `ObjectId`s are created close to observable ones,
  so a window of a few thousand values is plenty (the solver defaults are tuned for this).
- If a solver waits a long time after `docker compose up` before attacking, the boot-time
  timestamp anchor drifts — widen `--ts-window`. This is called out in the player `README.md`.

## Root cause (for the fix)

Use `crypto.randomBytes()` for anything security-sensitive (session tokens, reset tokens,
encryption keys). Never seed a PRNG with an `ObjectId` (or any timestamp/counter-derived
value), and never store an encryption key's seed next to its ciphertext.
