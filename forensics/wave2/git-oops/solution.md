# #48 "Git Oops" — Walkthrough (INTERNAL)

**Category:** Git · **Tier:** 🟢 Easy · **Artifact(s):** `repo.zip`
**Flag:** `Securinets{g1t_l0g_r3m3mb3rs_4ll}`

---

## What it teaches

| Skill | Why it matters |
|---|---|
| Git keeps history | A file deleted in a later commit still lives in the earlier one. Warm-up for #11 Force Push. |

---

## Intended path

### 1. Unzip and enter
`unzip -q repo.zip -d repo && cd repo`

### 2. Read the history
`git log --oneline` shows a commit `add deploy credentials (temp)` followed by `oops, remove committed credentials`.

### 3. Show the deleted content
`git log -p` (or `git show <sha-of-add-commit>`) prints the `deploy.key` that was added and then removed. `PRIVATE_TOKEN=` is the flag.

## Why grep/eyeball doesn't shortcut it
`grep -r` on the working tree finds nothing — the file was deleted from `HEAD`. You must read history.

---

## Hint ladder

1. **The current files don't have it. Where else does git store things?**
2. **`git log --oneline` — notice the 'add credentials' then 'remove credentials' pair.**
3. **`git log -p` and read the diff that ADDED deploy.key.**

---

## Build provenance
Real repo built with git: 4 commits (skeleton, add deploy.key, remove it, add app.py). The credential is reachable via `git log -p` — a deliberately EASIER cousin of #11 (which needs `reflog`/`fsck` for an UNREACHABLE commit).
