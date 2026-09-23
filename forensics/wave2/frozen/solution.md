# #23 "Frozen" — Walkthrough (INTERNAL)

**Category:** RE — PyInstaller / Python bytecode + crypto · **Tier:** 🟡🟠 Medium–Hard
**Artifact:** `activator.exe` (PyInstaller one-file, Python 3.9)
**Flag:** `Securinets{fr0z3n_pyc_st1ll_t4lks}`
**Derived secrets:** password `S3cur3_Sync_2026`, token `b7db6c8cd434a13c`

---

## What it teaches
Un-freezing a PyInstaller binary and reading Python bytecode. The secret is not a string in the
file — it is *computed* by convoluted code, so `strings` and "just run it" both fail. You have to
recover and read the source.

| Skill | Why it matters |
|---|---|
| `pyinstxtractor` (unpack PyInstaller) | Standard first move on any frozen Python exe |
| `pycdc` / decompiler on the `.pyc` | Recover readable source (decompyle3/uncompyle6 don't do 3.9 — pycdc does) |
| Tracing obfuscated key derivation | The password/token are built by code, across several pieces |
| Reproducing a home-rolled KDF + AES | Turn the derived pair into the flag |

---

## Intended path

### 1. Unpack
```
python pyinstxtractor.py activator.exe
```
→ `activator.exe_extracted/` with `activator.pyc` (the entry point pyinstxtractor names).

### 2. Decompile
`decompyle3`/`uncompyle6` reject 3.9 — use **pycdc** (Decompyle++):
```
pycdc activator.exe_extracted/activator.pyc
```

### 3. Read the derivation (this is the challenge)
```python
class _Cfg:
    A = 90; B = 7
    _s = [9,82,11,26,4,78,219,216,235,247,195,248,156,133,142,245]
    _legacy = [ ...,246 ]          # DECOY (last byte differs)
def _rk(i):  return (_Cfg.A + i*_Cfg.B) & 255
def _pw():   return bytes(_Cfg._s[i] ^ _rk(i) for i in range(len(_Cfg._s))).decode()
_SALT = ["ag","il","og"]
def _salt(): return ("".join(_SALT)+"ix").encode()          # b"agilogix"
def _tok(pw):
    h = pw.encode()+_salt()
    for _ in range(5000): h = sha256(h).digest()
    return h.hex()[:16]
```
- **password** = each `_s[i]` XOR the rolling key `(90 + 7*i) & 255` → `S3cur3_Sync_2026`.
- **token** = 5000-round SHA-256 of `password + "agilogix"`, first 16 hex → `b7db6c8cd434a13c`.
- **Trap:** `_legacy` looks like `_s` (only the last byte differs) → yields `S3cur3_Sync_2025`,
  whose token fails. Reading only `_legacy`, or skimming the salt assembly, gets you a wrong pair.

### 4. Unlock
The flag is AES-CBC, key = `sha256(pw + ":" + token)[:32]`, blob embedded (base64) as `_BLOB`.
Either run the exe and type the pair, or reimplement:
```
activator.exe
license password: S3cur3_Sync_2026
activation token: b7db6c8cd434a13c
→ Securinets{fr0z3n_pyc_st1ll_t4lks}
```

---

## Trick & red herring
- **Trick:** the pair is computed by code, not stored; only reading the decompiled logic yields it.
  Running blind is a dead end (the input gate re-derives and compares).
- **Red herring:** the `_legacy` list (one byte off) is a plausible-but-wrong password source.

---

## Build notes
Built with **Python 3.9** deliberately (pycdc/decompyle-class tools decompile 3.9 cleanly; 3.13/3.14
would degrade the challenge to raw `dis` reading). `make_activator.py` bakes the seed/decoy/token
and the AES blob into `activator.py`, then `pyinstaller --onefile`.

Verified as a fresh solver: `pyinstxtractor` → `pycdc` → derived pw/token purely from the decompiled
source → flag. Flag is **not** plaintext in the exe; no author identity or build path embedded
(`azizh`/`pulgaa`/`ch23`/`friendly-securinets` all 0). Answer key (`make_activator.py`, `activator.py`,
plaintext pw/token) stays in `build/ch23/`, not shipped.
