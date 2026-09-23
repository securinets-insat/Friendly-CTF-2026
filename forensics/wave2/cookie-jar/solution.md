# #13 "Cookie Jar" — Walkthrough (INTERNAL)

**Category:** Forensics · **Tier:** 🟢🟡 Easy–Medium · **Artifact:** `chrome_profile.zip` (Chromium profile)
**Flag:** `Securinets{h1st0ry_l1v3s_1n_th3_w4l}` (in the deleted URL's `session=` parameter)

---

## What it teaches

**"Cleared history" isn't gone** when the browser uses SQLite in WAL mode. The delete lives
in `History-wal` and hasn't been checkpointed into `History`, so opening the main DB alone
(ignoring the WAL) shows the pre-delete state. Same core technique as #24, applied to browser
forensics.

| Skill | Why it matters |
|---|---|
| Chromium profile layout (`History`, `Cookies`, `Bookmarks`) | Standard browser-forensics triage |
| SQLite WAL recovery (open without the `-wal`) | Recovering "deleted" browser records |
| Evidence preservation (work on a copy) | A checkpointing tool destroys the recovery |
| Reading a secret from a URL parameter | Tokens leak in query strings constantly |

---

## Intended path

### 1. Open the History DB
```
sqlite3 History "SELECT url,title FROM urls ORDER BY last_visit_time;"
```
Normal browsing (mail, wiki, portal, Google…) — but nothing incriminating. The `vault`
visit the story implies is absent: it was "cleared."

### 2. Notice it's WAL mode with a pending `-wal`
The profile ships `History`, `History-wal`, `History-shm`. Opening `History` normally replays
the WAL → the deletion is applied → the row stays hidden.

### 3. Recover: open the main DB without the WAL
```
cp History rec.db          # main file ONLY - no -wal / -shm
sqlite3 rec.db "SELECT url FROM urls WHERE url LIKE '%vault%';"
```
```
https://vault.agilogix.tn/unlock?session=Securinets{h1st0ry_l1v3s_1n_th3_w4l}
```
The `session=` parameter is the flag.

> **Preserve first.** Opening the shipped `History` with a GUI (DB Browser) that
> auto-checkpoints writes the delete into the main file — the row is then gone for good. Work
> on copies; the README warns players.

---

## The red herrings

- **`Bookmarks`** contains plausible internal links, including `vault.agilogix.tn/login`
  (not the flag) and a `reset?token=RESET_7c1e94ab` — real-looking but worthless.
- **`Cookies`** has ordinary session cookies (`SID`, `csrftoken`, `NID`) — scenery that looks
  worth checking but holds nothing.

---

## Alternative paths (all valid)

- `strings History | grep vault` — the deleted row's bytes persist as a free cell in the main
  DB page (pre-delete state), so a quick strings/grep also finds it. The WAL method is the
  "clean" intended path; this is the pragmatic one.
- A SQLite WAL/freelist recovery tool (`walitean`, manual frame parsing).
- `sqlite3 History-wal` inspection, or `.recover` on a copy.

No guessing — the URL is recoverable multiple ways.

---

## Hint ladder

1. **"They cleared history — but Chromium uses SQLite in WAL mode. What's in the
   `History-wal` file, and what happens if you open `History` *without* it?"**
2. **"Copy `History` alone (leave the `-wal` behind) and query the `urls` table for what was
   removed. Ignore the bookmarks/cookies decoys."**
3. **"`cp History rec.db; sqlite3 rec.db \"SELECT url FROM urls WHERE url LIKE '%vault%'\"` —
   the flag is the `session=` parameter."**

---

## Failure modes

| Symptom | Cause / fix |
|---|---|
| Recovery returns nothing | The `History` was opened by a checkpointing tool first. Re-extract; copy the main DB before opening anything. |
| Player submits the `Bookmarks` vault link / reset token | Red herrings. The real URL is the *deleted* one in `urls`. |
| GUI browser shows history "empty" | Expected — it replays the WAL. Work on the main file alone. |

---

## Build provenance

- Hand-built Chromium `History` (realistic `urls`/`visits` schema, WebKit microsecond
  timestamps) via `build-ch13.py`: insert history incl. the secret vault URL → checkpoint
  (rows into main DB) → fresh connection with `wal_autocheckpoint=0` → delete the vault row →
  copy the `History`/`-wal`/`-shm` trio while that connection is still open (delete lives in
  the WAL, row still in main DB). Plus a `Cookies` DB and `Bookmarks` decoy.
- Verified on the shipped profile: with the `-wal`, the vault rows are gone (`count=0`);
  main-DB-only recovery returns the URL with the flag.

**Difficulty dial:** skip the pre-delete checkpoint so the row exists *only* in the WAL (kills
the `strings` shortcut, forcing genuine WAL-frame parsing). Kept the robust dual-path version
for this tier — it mirrors #24's mechanism in a browser context.
