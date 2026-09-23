# #51 "Bookmark" — Walkthrough (INTERNAL)

**Category:** Browser forensics · **Tier:** 🟢 Easy · **Artifact(s):** `places.sqlite`
**Flag:** `Securinets{br0ws3r_db_1s_just_sql1t3}`

---

## What it teaches

| Skill | Why it matters |
|---|---|
| Browser data is just SQLite | Read it with any SQLite tool. Warm-up for #13 Cookie Jar. |

---

## Intended path

### 1. Open the DB
`sqlite3 places.sqlite` (or DB Browser for SQLite).

### 2. Query places
`SELECT url,title FROM moz_places;` — a `vault-login` row has a URL with `?token=Securinets{...}`.

### 3. Read the flag
The token in that URL is the flag.

---

## Hint ladder

1. **A places.sqlite is a database. Open it as one.**
2. **`sqlite3 places.sqlite 'SELECT url FROM moz_places;'`**
3. **The `vault` bookmark URL has a `token=` — that's the flag.**

---

## Build provenance
SQLite with `moz_places` + `moz_bookmarks`. Flag in a bookmarked URL's `token=` parameter, among ordinary bookmarks. Plain `SELECT` — no WAL/freelist recovery (that's #13).
