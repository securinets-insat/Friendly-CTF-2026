# Reset Vault

**Difficulty:** Medium
**Tags:** `mongodb`, `objectid`, `weak-prng`, `logic-flaw`, `token-prediction`

## Story

The Vault is a note-taking app for people who don't trust their memory —
or, judging by the changelog, their password. Register an account, jot
down a few notes, encrypt the ones that matter. The admin has one note
they'd rather nobody else read.

Everything about login, sessions, and note storage works exactly the way
you'd expect. Look somewhere else.

## Getting started

```
docker compose up --build
```

The app is served on **http://localhost:3000**. The database is not
reachable from outside the container network — there's nothing to gain
by pointing a client at it directly.

Register your own account and explore the app for a while before you
start scripting anything.

Note: the admin account (and its note) is created the moment the container
boots. If your exploit involves guessing *when* something was created,
the longer you wait between starting the instance and running your
script, the wider that search window needs to be — you'll have an easier
time if you don't let it sit idle for too long before attacking.

## What this challenge is *not*

No SQL/NoSQL injection is required anywhere in the intended solve. If
you find yourself trying `$ne` payloads in login forms, you're spending
time on the wrong door.

## Flag format

```
Securinets{...}
```

The flag is generated fresh on every container boot (a random hex string
inside the `Securinets{}` wrapper) — it is not hardcoded anywhere in this
repo, so each deployed instance has its own unique flag.

## Hints

Staged hints (release order, if running on a platform that supports it):

1. The reset token doesn't come from `crypto.randomBytes`. Where does its
   randomness actually come from?
2. MongoDB document IDs aren't as random as they look. What's inside a
   12-byte ObjectId?
3. You can see one of these generated values right now, in your own
   browser, without asking the server for anything.
4. Check the app's dependencies — one of them is doing the "randomness"
   for more than one feature.
