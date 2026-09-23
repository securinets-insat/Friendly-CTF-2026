# #11 "Force Push" — Walkthrough (INTERNAL)

**Category:** Forensics · **Tier:** 🟢🟡 Easy–Medium · **Artifact:** `repo.zip` (44 KB)
**Flag:** `Securinets{g1t_r3fl0g_n3v3r_f0rg3ts}`

---

## What it teaches

The real lesson is **unreachable is not deleted**. Git is a content-addressed object
store; branches are just pointers into it. Moving a pointer does not remove what it used
to point at.

Concretely, a player walks away knowing:

| Skill | Why it matters outside the CTF |
|---|---|
| `git reflog` recovers rolled-back branch positions | The standard "I destroyed my work with `reset --hard`" rescue |
| `git fsck --no-reflogs --lost-found` finds orphaned objects | How you audit a repo you were handed, with no reflog |
| `git show <sha>:<path>` reads a file without checkout | Inspecting history without disturbing the working tree |
| Force-pushing does **not** unpublish a secret | The single most important operational takeaway |

That last row is the point of the whole task. Every real credential leak ends with
someone saying "it's fine, I force-pushed" — and it is not fine. The only fix is
rotation. This challenge makes players prove that to themselves.

---

## Intended path

### 1. Look at what is obviously there

```
unzip repo.zip && cd logi-api
git log --oneline
```

```
10d632c gitignore secrets, add example config, rotate keys
8380564 add api tests
ad1ff23 add shipment lookup endpoint
239047f add yaml config loader
0d0f9c4 initial commit: health endpoint
```

Five commits, nothing incriminating. A naive `grep -r Securinets .` returns nothing,
because the only copy lives in a compressed git object.

### 2. Read the scenery

`DEPLOY.md` contains the breadcrumb:

> 2026-01-23: all production credentials were rotated. The old master token in
> `config/keys/legacy_api.key` is expired and kept only for the v1 client shim.

This confirms a leak happened and dates it. It also baits the red herring (below).

### 3. Realise the history is shorter than the story

The commit dates jump **2026-01-12 → 2026-01-23**, with three commits landing inside
half an hour on the 23rd. A repo where a third of the history appears in one burst,
right when `DEPLOY.md` says credentials were rotated, is a repo whose history was
rewritten.

### 4. Recover — path A, reflog

```
git reflog
```

```
10d632c HEAD@{0}: commit: gitignore secrets, add example config, rotate keys
8380564 HEAD@{1}: commit: add api tests
ad1ff23 HEAD@{2}: commit: add shipment lookup endpoint
239047f HEAD@{3}: reset: moving to HEAD~3          <-- the rewrite
e585199 HEAD@{4}: commit: add api tests
267dcdb HEAD@{5}: commit: add shipment lookup endpoint
a5b056e HEAD@{6}: commit: add production credentials for deploy   <-- there it is
239047f HEAD@{7}: commit: add yaml config loader
```

```
git show a5b056e:config/secrets.yml
```

```yaml
# production credentials - DO NOT COMMIT
database:
  host: db-prod-01.agilogix.internal
  user: logi_api
  password: Tr0ub4dour&3-prod
aws:
  access_key_id: AKIA4YFAKE2XMPLQ7T3B
  secret_access_key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
api:
  master_token: Securinets{g1t_r3fl0g_n3v3r_f0rg3ts}
```

### 5. Recover — path B, fsck

```
git fsck --no-reflogs --lost-found
```

```
dangling commit e58519986873524af022350a00c965a4061cae9e
```

```
git log --oneline e58519986873      # walk back from the orphaned tip
git show a5b056e:config/secrets.yml
```

> **`--no-reflogs` is required.** Plain `git fsck` treats reflog entries as reachable
> roots, so it reports *nothing* dangling while the reflog exists. A player who tries
> `git fsck --lost-found`, sees empty output, and concludes the repo is clean has been
> misled by their own tool — not by us. This is authentic behaviour and worth explaining
> in the post-event writeup.

---

## The red herring

`config/keys/legacy_api.key`:

```
legacy_master_token: SEC_5f3a91c4e77b28d0a1449e6b3cc80f12
```

Findable in seconds with `grep -ri token .`, correctly shaped, and sitting in the current
checkout where players look first. `DEPLOY.md` explicitly calls it expired — so it is
*fair*, not a troll: the information needed to dismiss it is right there. It costs time
only to players who grep before they read.

`config/secrets.example.yml` plays the same role more gently — all `CHANGEME`, obviously
a template.

---

## Alternative paths that legitimately work

- `git cat-file --batch-all-objects --batch-check` then filtering for blobs, and reading
  each. Brute-force but valid — the repo is small enough.
- `git log -g --all -p` (reflog-walking with patches) dumps the secret directly.
- Unpacking `.git/objects` by hand with `zlib` in Python. Slow, but a player who does not
  know `reflog` can still get there.

All acceptable. None require guessing.

---

## Hint ladder

1. **"`git log` shows you what is reachable. It does not show you everything git stores."**
2. **"The branch was rolled back. Git keeps a record of every position a branch has ever
   held — locally."**
3. **"`git reflog`. Then `git show <commit>:config/secrets.yml`."**

---

## Failure modes

| Symptom | Cause |
|---|---|
| `git reflog` is empty | Player cloned the repo instead of using it in place. Reflog is local and does not transfer. Tell them to work in the extracted directory. |
| `git fsck --lost-found` shows nothing | Expected — see the `--no-reflogs` note above. |
| Challenge is dead on arrival | `git gc --prune=now` was run in the build repo. This deletes the unreachable object permanently. **Never run it.** |
| Player submits `SEC_5f3a91c4...` | Red herring working as designed. |

---

## Build provenance

- Build tree: `build/ch11/logi-api/` (working clone, shipped) and `build/ch11/origin.git`
  (bare remote, **not shipped**)
- Identity in commits: `Mehdi Trabelsi <m.trabelsi@agilogix.tn>` — fictional, verified no
  real-author leakage
- All file mtimes forced to `2026-01-23T09:41:00` so the zip listing agrees with the commit dates

**Hard-mode variant, free:** ship `origin.git` instead. Bare repos disable reflog by
default (`core.logAllRefUpdates=false`), so path A vanishes and players must use
`git fsck --lost-found` — which *does* work there, since there is no reflog to mask it.
Keep this in reserve if Tier 2 lands too soft.
