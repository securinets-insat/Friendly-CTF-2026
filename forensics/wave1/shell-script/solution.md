# #53 "Shell Script" — Walkthrough (INTERNAL)

**Category:** File types · **Tier:** 🟢 Easy · **Artifact(s):** `Flag.pdf`
**Flag:** `Securinets{sh4r_1s_4_sh3ll_4rch1v3}`

---

## What it teaches

| Skill | Why it matters |
|---|---|
| Check every layer with `file` | A shar (shell archive) masquerading as a PDF unpacks to a gzip that holds the flag. |

---

## Intended path

### 1. Identify
`file Flag.pdf` -> `shell archive text`, not a PDF. It's a self-extracting `/bin/sh` script.

### 2. Unpack it
`sh Flag.pdf` writes `secret.gz`. (Read the script first — it only does a `base64 -d` into a file; safe.)

### 3. Decompress
`file secret.gz` -> gzip. `gunzip secret.gz && cat secret` -> the flag.

## Why grep/eyeball doesn't shortcut it
Running it blind isn't needed — the script is short and readable; it just base64-decodes an embedded gzip.

---

## Hint ladder

1. **The extension says PDF. Does `file` agree?**
2. **It's a shell archive (shar). Run it with sh (after reading it) to unpack.**
3. **It produces secret.gz — gunzip it and cat the result.**

---

## Build provenance
A POSIX shar: `/bin/sh` script that `base64 -d`s an embedded gzip of the flag into `secret.gz`. `file` reports `shell archive text`.
