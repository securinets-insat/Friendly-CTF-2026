# #44 "Hash Hunt" — Walkthrough (INTERNAL)

**Category:** Misc · **Tier:** 🟢 Easy · **Artifact(s):** `samples.zip`, `TARGET_HASH.txt`
**Flag:** `Securinets{h4sh_m4tch3s_th3_f1l3}`

---

## What it teaches

| Skill | Why it matters |
|---|---|
| Hashes as fingerprints | Identifying one file out of many by content hash. |

---

## Intended path

### 1. Unpack
`unzip -q samples.zip`

### 2. Hash everything and match
```
sha256sum sample_*.txt | grep "$(head -1 <TARGET_HASH.txt; tail -1 TARGET_HASH.txt)"
```
or simply `sha256sum sample_*.txt | grep <hash-from-file>`.

### 3. Read the flag
`cat` the matching file; its `operator note:` line is the flag.

## Why grep/eyeball doesn't shortcut it
Every file looks like `operator note: Securinets{...}`; only the one whose hash matches is real. You cannot eyeball it.

---

## Hint ladder

1. **The description/`TARGET_HASH.txt` gives you a SHA-256. Of what?**
2. **Hash all 300 files and compare.**
3. **`sha256sum sample_*.txt | grep <the hash>` then read that file.**

---

## Build provenance
300 files each with a distinct fake `Securinets{f4k3_...}`; one real flag. `TARGET_HASH.txt` carries the real file's SHA-256.
