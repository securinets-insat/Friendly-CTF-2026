# #49 "Hidden Files" — Walkthrough (INTERNAL)

**Category:** Linux · **Tier:** 🟢 Easy · **Artifact(s):** `home_backup.tar.gz`
**Flag:** `Securinets{d0tf1l3s_h1d3_1n_pl41n_s1ght}`

---

## What it teaches

| Skill | Why it matters |
|---|---|
| Dotfiles are hidden by default | `ls` skips them; `ls -a`/`find` don't. |

---

## Intended path

### 1. Extract
`tar xzf home_backup.tar.gz`

### 2. Show hidden files
`ls -laR home/` or `find home -name '.*'` reveals `home/analyst/.config/.secret/.flag`.

### 3. Read the flag
`cat home/analyst/.config/.secret/.flag`.

---

## Hint ladder

1. **A plain `ls` won't show everything.**
2. **Look for files and folders starting with a dot.**
3. **`find home -name '.*' -type f` -> read the `.flag`.**

---

## Build provenance
tar.gz of a fake home dir; flag in `~/.config/.secret/.flag` (nested hidden dir), among ordinary files.
