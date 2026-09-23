# #24 "Signal Lost" — Walkthrough (INTERNAL)

**Category:** Forensics · **Tier:** 🟡🟠 Medium-Hard
**Artifact:** `android_extraction.zip` (100 KB) — a partial filesystem extraction
**Flag:** `Securinets{wal_r3wind_m4g1c_by73s_st3g0}`
**Vault pin (in shared_prefs):** `4471-vault`

A three-stage chain, each stage feeding the next:
1. **SQLite WAL** — a deleted message row, recoverable by ignoring the `-wal`
2. **File repair** — the referenced image has a destroyed magic header and a wrong extension
3. **Append stego + crypto** — an AES blob after the PNG's `IEND`, keyed by a pin from prefs

---

## What it teaches

Three different "it's gone / it's hidden" mechanisms in one realistic mobile artifact, and
the discipline that mobile forensics actually demands.

| Skill | Why it matters outside the CTF |
|---|---|
| SQLite **WAL** internals: uncheckpointed changes live in `-wal`, not the main DB | The #1 source of "deleted" chat messages on modern phones |
| **Evidence preservation** — never open the original with a writing tool | The single most common way analysts destroy their own evidence |
| Repairing file **magic bytes** / spotting a wrong extension | Recovering renamed or partially-wiped media |
| **Appended-data** carving after a container's real end marker | Classic file-in-file stego |
| Pulling secrets from Android `shared_prefs` XML | Where apps really keep tokens/pins |

---

## Intended path

### 1. SQLite WAL — recover the wiped message

The chat thread in `databases/msgstore.db` looks clean when opened normally, because the app
is in **WAL mode** and the deletion was committed to the `-wal` but never checkpointed into
the main database. Opening the DB the ordinary way replays the WAL → the row stays hidden.

**The move:** set the `-wal` (and `-shm`) aside and open the *main file alone*. With no WAL to
replay, SQLite shows the last checkpointed state — which still contains the deleted row.

```
cp databases/msgstore.db recovery.db        # main file ONLY - no -wal, no -shm
sqlite3 recovery.db "SELECT sender, body, media_name FROM message WHERE media_name IS NOT NULL;"
```

```
pulgaa|IMG-20190614-WA0007.jpg - the pin is saved in the app settings like always|IMG-20190614-WA0007.jpg
```

Two things fall out: the **filename** `IMG-20190614-WA0007.jpg`, and the hint that the
**pin is in the app settings** (→ `shared_prefs`).

> **Preserve first.** If a player opens the shipped `msgstore.db` with a GUI (DB Browser,
> etc.) that auto-checkpoints, it writes the deletion into the main file and the row is gone
> for good. The README warns to work on copies. This is the authentic mobile-forensics
> lesson, and it bit the *author's own verification* three times — leave it in.

### 2. The referenced file won't open

```
file Media/IMG-20190614-WA0007.jpg
```

```
Media/IMG-20190614-WA0007.jpg: data          # not a JPEG at all
```

```
xxd Media/IMG-20190614-WA0007.jpg | head -2
```

```
00000000: 0000 0000 0000 0000 0000 000d 4948 4452   ............IHDR
00000010: 0000 01bf 0000 01bf 0802 0000 0047 714e   .............GqN
```

The `.jpg` name is a lie, and the first 8 bytes are zeroed — but `IHDR` at offset 12 is the
PNG header chunk. This is a PNG with a **destroyed signature**. Restore the 8 magic bytes:

```
printf '\x89PNG\r\n\x1a\n' | dd of=Media/IMG-20190614-WA0007.jpg bs=1 count=8 conv=notrunc
file Media/IMG-20190614-WA0007.jpg
```

```
PNG image data, 447 x 447, 8-bit/color RGB, non-interlaced       # opens now
```

### 3. Appended blob → decrypt with the prefs pin

The repaired PNG has extra data after its `IEND` end-of-image chunk. Carve it:

```
python3 -c "d=open('Media/IMG-20190614-WA0007.jpg','rb').read(); i=d.rfind(b'IEND')+8; open('blob.enc','wb').write(d[i:])"
xxd blob.enc | head -1        # 'Salted__' -> OpenSSL encryption
```

The pin and cipher come from `shared_prefs`:

```
grep -oP '(media_vault_pin|backup_cipher)">\K[^<]+' shared_prefs/com.agilogix.messenger_preferences.xml
# 4471-vault   /   aes-256-cbc
```

```
openssl enc -d -aes-256-cbc -pbkdf2 -in blob.enc -pass pass:4471-vault
```

```
Securinets{wal_r3wind_m4g1c_by73s_st3g0}
```

(`binwalk`/`foremost` also flag the `Salted__` trailer, so carving has more than one route.)

---

## The red herring

`Media/IMG-20190612-WA0003.jpg` is a **valid** PNG (mislabeled `.jpg`) that opens
immediately — unlike the real target, which is broken. A player who lists the media folder
and opens the one that *works* sees a legitimate-looking image with **nothing appended**
(zero bytes after `IEND`) and no connection to the recovered filename. It's the "thumbnail
cache" decoy: the working file is the trap, the broken file is the goal.

---

## Alternative paths that legitimately work

- **Stage 1 via `strings`/carving:** the deleted row's bytes persist as an unallocated cell
  in the main DB page, so `strings msgstore.db | grep IMG-` finds the filename without WAL
  reasoning. A legitimate pragmatic route; the WAL method is the "clean" one. (Only works on
  a preserved copy — a checkpointed file may overwrite the free cell.)
- **Stage 1 via a WAL parser** (`sqlite3_analyzer`, `walitean`, manual frame parsing) —
  reads the deletion out of the `-wal` directly.
- **Stage 3 via `binwalk -e`** — extracts the `Salted__` blob automatically.

No guessing: the pin is handed over by `shared_prefs`, the cipher is named there too.

---

## Hint ladder

1. **"The messages look clean, but this app uses SQLite in WAL mode. What does the `-wal`
   file hold, and what happens if you open the database *without* it?"**
2. **"You have a filename and a note that the pin is 'in app settings'. The file won't open —
   look at its first bytes against what its extension claims. And `shared_prefs` is where
   Android apps keep settings."**
3. **"Fix the PNG signature (`89 50 4E 47 0D 0A 1A 0A`). Everything after `IEND` is an
   OpenSSL (`Salted__`) blob — `openssl enc -d -aes-256-cbc -pbkdf2 -pass pass:<the pin>`."**

---

## Failure modes

| Symptom | Cause / fix |
|---|---|
| Recovery returns nothing | The main DB was opened by a checkpointing tool first, applying the delete. Re-extract, snapshot the main file **before** opening anything. |
| Player opens the decoy, finds nothing, concludes it's broken | Red herring working. The recovered filename is `WA0007`, not `WA0003`. |
| `file` says "data", player gives up | Hint 2 — compare the header to the claimed type; `IHDR` is visible. |
| `openssl` "bad decrypt" | Wrong pin, or blob boundary off by the 4-byte `IEND` CRC. Carve from `rfind('IEND')+8`. |
| GUI SQLite browser shows the row deleted | Expected — it replays/updates the WAL. Work on the main file alone. |

---

## Build provenance

- Build tree: `build/ch24/` — `cover.jpg/ppm`, `real.png`, `flag.txt`, `flag.enc`,
  `with_blob.png`, `src.db*`, loose `IMG-*.jpg`; **none shipped**. `dist/24-signal-lost/`
  holds only `android_extraction.zip`, `README.md`, `SHA256SUMS`.
- Carrier: the **real Securinets logo** (`securinets.jpg`) → `djpeg` → PPM → re-encoded to
  PNG (pure-Python zlib), per the real-assets preference. Not a synthetic gradient.
- WAL state built with the connection-open technique: insert → `wal_checkpoint(TRUNCATE)`
  (rows land in main DB) → fresh connection with `wal_autocheckpoint=0` → `DELETE` → copy the
  trio while still open (delete lives in `-wal`, row still in main DB).
- Flag: `openssl aes-256-cbc -pbkdf2` appended after `IEND`; pin `4471-vault` and cipher name
  placed in `shared_prefs`.
- Verified **from the shipped zip**: default open hides the media rows (0); main-DB-only
  recovery returns the filename; target file still header-corrupted; flag absent as plaintext.

**Difficulty dial:** to harden, remove the `strings` fallback by making the deleted row only
present in the `-wal` (skip the pre-delete checkpoint so it's never in a main-DB free cell),
forcing genuine WAL-frame parsing. Kept the robust dual-path version here.
