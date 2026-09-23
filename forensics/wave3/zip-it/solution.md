# #14 "Zip It" — Walkthrough (INTERNAL)

**Category:** Forensics · **Tier:** 🟢🟡 Easy–Medium
**Artifacts:** `evidence.zip` (12 KB) + `securinets.jpg` (11 KB, the known plaintext)
**Flag:** `Securinets{kn0wn_pl41nt3xt_b34ts_brut3_f0rc3}`
**Archive password (author record):** in `build/ch14/.password_used` — 28 random chars, never shipped

---

## What it teaches

**Legacy ZipCrypto is broken against known plaintext.** The traditional PKWARE cipher
(everything before WinZip's AES) leaks its internal state if you know *any* ~12+ contiguous
plaintext bytes of an encrypted entry. Biham & Kocher's attack, implemented in `bkcrack`,
recovers the three 32-bit internal keys — which then decrypt *every other file in the same
archive*, no password required.

| Skill | Why it matters outside the CTF |
|---|---|
| Telling ZipCrypto from AES-256 (`7z l -slt`, `zipdetails`) | Decides whether an archive is attackable at all |
| Recognising a known-plaintext opportunity | The core insight — you rarely need the password |
| Driving `bkcrack` (`-c`/`-p` attack, `-U` re-lock) | The standard tool for this exact situation |
| Knowing when brute force is pointless | Stops players burning hours on `john`/`fcrackzip` |

The lesson players walk away with: **"password-protected zip" says nothing about security.**
If it's the old format and one member is predictable, the password is irrelevant.

---

## Intended path

### 1. Fail at the obvious thing (correctly)

```
unzip evidence.zip           # prompts for a password
```

The zip comment offers bait:

```
Password hint: it's one of the ops team's usual passphrases - try rockyou.
```

A player who takes that at face value runs `fcrackzip -D -p rockyou.txt evidence.zip` or
`john` — and gets nothing, because the real password is 28 random characters. This is meant
to happen; it teaches that guessing is the wrong tool here.

### 2. Identify the cipher

```
7z l -slt evidence.zip | grep -iE "Method|Encrypted|Name"
```

```
Name = securinets.jpg
Method = ZipCrypto Store           <-- legacy PKWARE, and STORED (uncompressed)
Name = notes.txt
Method = ZipCrypto Deflate:Maximum
```

`ZipCrypto` (not `AES-256`) is the green light. That `securinets.jpg` is **Store**d is the second
gift: its encrypted bytes are the raw JPEG, so the known plaintext lines up with zero
deflate in the way.

### 3. Realise you already hold the plaintext

The challenge *hands the player `securinets.jpg`* and the story explains why: it's the company's
public logo, the same file that's in the locked archive. So the player possesses the exact
plaintext of one encrypted member. That is the whole attack.

### 4. Run bkcrack

```
bkcrack -C evidence.zip -c securinets.jpg -p securinets.jpg
```

```
[..] Z reduction using 11404 bytes of known plaintext
[..] Attack on 35 Z values at index 80657
Keys: edd5f7a3 ba9605d6 194c46bb
Found a solution. Stopping.
```

**Wall time: ~5 seconds** (measured, 2 cores). With ~11 KB of stored plaintext the
Z-reduction is near-instant. It will be fast on any player hardware — no risk of timeout
abandonment.

### 5. Use the keys to get the flag

The cleanest route — re-lock the archive with a known password, which also handles the
DEFLATE on `notes.txt` automatically:

```
bkcrack -C evidence.zip -k edd5f7a3 ba9605d6 194c46bb -U solved.zip newpass
unzip -P newpass solved.zip
cat notes.txt
```

```
vault_unseal_key: Securinets{kn0wn_pl41nt3xt_b34ts_brut3_f0rc3}
```

(Alternative: `bkcrack -c notes.txt -k <keys> -d notes.deflate` then inflate with
`python3 -c "import zlib,sys;sys.stdout.buffer.write(zlib.decompress(open('notes.deflate','rb').read(),-15))"`.
The `-U` route is friendlier and worth pointing at in a hint if someone gets stuck here.)

---

## The red herrings (both fair)

1. **The zip comment** ("try rockyou"). Steers toward a wordlist attack that cannot succeed
   — the password is random. It costs time only to players who attack the password instead
   of the cipher, which is precisely the misconception the challenge corrects.
2. **The password's randomness itself.** There is genuinely no password shortcut. This is
   design, not cruelty: it forces the intended path rather than rewarding a lucky guess and
   letting a player skip the lesson.

Neither is a troll — the information to move past both (ZipCrypto + a provided plaintext) is
present and sufficient.

---

## Alternative paths that legitimately work

- Attacking `notes.txt` directly instead of via `-U`, then inflating by hand (above).
- Using bkcrack's `-p` with an *offset* if a player only recognises a fragment of the PNG
  (e.g. the fixed JPEG SOI + JFIF header bytes) — slower, more key candidates, but valid.
  This is the "harder mode" that exists automatically if you ever ship a *compressed* logo.
- Recovering the original password from the keys (`bkcrack -k <keys> -r 12 ?p`) — unnecessary
  here and slow, but some players do it for completeness.

No guessing path exists, by design.

---

## Hint ladder

1. **"Is it worth attacking the password? Check the archive first — how is it encrypted,
   and what *else* is in it that you might already have?"**
2. **"ZipCrypto (not AES) plus a file whose exact contents you possess = known-plaintext
   attack. The tool is `bkcrack`."**
3. **"`bkcrack -C evidence.zip -c securinets.jpg -p securinets.jpg` → then `-k <keys> -U out.zip pw`
   and unzip normally."**

---

## Failure modes

| Symptom | Cause / fix |
|---|---|
| `bkcrack` finds no solution | Player's `securinets.jpg` isn't byte-identical to the zip's copy. Ours are the same file — confirmed by the successful attack. |
| Player stuck after recovering keys | They don't know `-U`. Nudge with hint 3's second half. |
| `unzip -p evidence.zip securinets.jpg` hangs (authors) | The entry is encrypted; `unzip -p` blocks on a password prompt. Verify KPA validity via the attack itself, not by extracting. |
| Player spends an hour in `john` | Red herring #1 working. Fair game. |
| Someone submits `stg_...`-style bait | N/A here — no fake flag inside; the only secret is the real one. |

---

## Build provenance

- Build tree: `build/ch14/` — contains `.password_used`, `notes.txt`, `known_plain.png`,
  `attack.log`, `solved.zip`; **none shipped**. Verified `dist/14-zip-it/` holds only
  `evidence.zip`, `securinets.jpg`, `README.md`, `SHA256SUMS`.
- `securinets.jpg` is the real Securinets logo (447×447 JPEG, supplied by the author).
  Stored uncompressed in the archive so the KPA is clean and fast.
- Encryption forced to ZipCrypto by using `zip -P` (not `7z`, which defaults to AES).
  `securinets.jpg` added with `-0` (store), `notes.txt` with `-9` (deflate).
- Flag confirmed **absent** from the ciphertext (`grep -a Securinets evidence.zip` → nothing);
  red-herring comment confirmed present.

**Difficulty dial:** if solves come too fast, ship the logo *compressed* (`zip -9`) instead
of stored. bkcrack still works but the player must supply the correctly-deflated plaintext
(or attack via the JPEG header at an offset), which is a real step up. Kept stored here so
Easy–Medium stays Easy–Medium.
