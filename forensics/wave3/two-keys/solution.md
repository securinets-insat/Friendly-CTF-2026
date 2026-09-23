# #21 "Two Keys" — Walkthrough (INTERNAL)

**Category:** Memory forensics + RE (dynamic) · **Tier:** 🟡🟠 Medium–Hard
**Artifact:** `mem.raw.zst` (VirtualBox `dumpvmcore` ELF core, ~2 GB uncompressed)
**Flag:** `Securinets{sh3llc0d3_1n_h34p_run_w1th_pw_t0k3n}`
- **partA** `sh3llc0d3_1n_h34p` — emulate the heap shellcode with **scdbg**
- **partB** `run_w1th_pw_t0k3n` — decompile `updater.exe`, decode the password, run it with password+token

---

## What it teaches
One RAM image, two independent recovery techniques against the same sample:
malfind → shellcode emulation, and PE carving → .NET decompilation → dynamic execution.

| Skill | Where |
|---|---|
| Vol3 process triage | `windows.pslist` → `updater.exe` |
| `malfind` + shellcode emulation (scdbg) | the RWX heap region → **partA** |
| Carving a PE from memory (`dumpfiles`) | recover `updater.exe` |
| .NET decompilation (dnSpy/ILSpy) | read `ep`/`tk`/`DecPw()`/`Main` |
| Dynamic execution to unlock a secret | run with the two keys → **partB** |

---

## Intended path

### 1. Find the process
```
vol -f mem.raw windows.pslist | grep -i updater      # -> updater.exe  PID 444
```

### 2. partA — the heap shellcode → scdbg
```
vol -f mem.raw windows.malfind --pid 444 --dump
```
Two RWX regions dump; the small one begins `fc e9 a5 00 …` (`cld; jmp …`, then `push 0x876F8B31`
= the WinExec block-API stub). Emulate it (scdbg is a Windows tool — give it a **Windows** path):
```
scdbg.exe /f pid.444.vad.0x2790000-0x2790fff.dmp
   -> WinExec("cmd /c echo part1:sh3llc0d3_1n_h34p")
```
→ **partA = `sh3llc0d3_1n_h34p`**. (The other RWX region is .NET/heap noise — the red herring.)

### 3. partB — carve the PE, decompile, run it
```
vol -f mem.raw windows.dumpfiles --pid 444        # -> ...ImageSectionObject.updater.exe.img
mv *ImageSectionObject.updater.exe.img updater.exe
```
Open `updater.exe` in **dnSpy** (in a Defender-off sandbox — it carries the shellcode). The class
is self-documenting:
```csharp
static string ep = "FGsuKGoJIzQ5e2hqaGw=";   // encoded password
static string tk = "SESSTOK-8f3a2b9c1d0e";   // token (plaintext)
static string DecPw(){ ... x[i]^0x5A ... }    // base64 -> XOR 0x5A
static void Main(string[] a){ ... if (a[0]==DecPw() && a[1]==tk){ print XOR(bl, sha256(a0:a1)) } }
```
Decode the password and run it with the two keys:
```
python3 -c "import base64;print(''.join(chr(b^0x5A) for b in base64.b64decode('FGsuKGoJIzQ5e2hqaGw=')))"
   -> N1tr0Sync!2026
updater.exe "N1tr0Sync!2026" "SESSTOK-8f3a2b9c1d0e"
   -> run_w1th_pw_t0k3n
```
→ **partB = `run_w1th_pw_t0k3n`**.

### 4. Combine
`Securinets{sh3llc0d3_1n_h34p_run_w1th_pw_t0k3n}`

---

## Trick & red herrings
- **Trick:** the two halves need two *different* skills — a static/emulation path (scdbg) and a
  dynamic path (run the carved binary). Neither shortcuts the other.
- **Shellcode is not a freebie in the exe:** it's XOR-encoded (`sc` ^ `kk`) and only decoded into
  the RWX region at runtime — `scdbg` on the raw exe bytes yields garbage, so partA genuinely comes
  from **memory** (the decoded region) or from reversing the decoder.
- **Red herring:** `malfind` reports two RWX regions; the 64 KB one (`0x27a0000`, begins `2b 2b 54 dd`)
  is .NET/heap, not shellcode.

---

## Build notes
Built on `ctf-win` `golden-nodef` (Defender off). `gen_shellcode.py` assembles a WinExec block-API
stub with **keystone** (partA rides in the `WinExec` CMD; scdbg-verified) — no msfvenom/sudo needed.
`make_updater.py` bakes the **encoded** shellcode + `enc_pw` (base64∘xor0x5A) + token + XOR'd partB
into a **comment-free** `updater.cs`; compiled in-guest with `csc /platform:x86` (host Defender
quarantines it — expected). Ran hold-mode, captured with `VBoxManage debugvm dumpvmcore`.

Verified end-to-end from the dump: `pslist`→`malfind`→scdbg = partA; `dumpfiles`→run = partB;
ship-gate negatives — `Securinets{` = 0 and `run_w1th_pw_t0k3n` = 0 in the raw dump (only the partA
fragment appears, inside the decoded shellcode, by design). Answer key (`make_updater.py`, plaintext
pw/flag) stays in `build/ch21`, not shipped.
