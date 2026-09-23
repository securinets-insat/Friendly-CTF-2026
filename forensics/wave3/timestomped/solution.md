# #18 "Timestomped" — Walkthrough (INTERNAL)

**Category:** Forensics (Windows anti-forensics) · **Tier:** 🟡🟠 Medium–Hard
**Artifacts:** `$MFT`, `$LogFile`, `$J` (`$UsnJrnl`), `Amcache.hve` (in `timestomp_triage.zip`)
**Flag:** `Securinets{si_backdated_fn_never_lies}` (resident in the tampered file's `$MFT` record)

---

## What it teaches

Detecting **timestomping**, not recovering deleted data. `SetFileTime` (the API behind every
timestomp tool) rewrites the `$STANDARD_INFORMATION` (`$SI`) timestamps but **cannot touch
`$FILE_NAME` (`$FN`)** — the OS owns `$FN`. So a backdated file betrays itself: `$SI` ≪ `$FN`.
The USN journal then gives the ground truth independently.

| Skill | Why it matters |
|---|---|
| `MFTECmd` — `$SI` vs `$FN` comparison | The core anti-forensics tell |
| USN `$J` analysis (`MFTECmd -f $J`) | Independent true-time corroboration |
| Distinguishing malicious backdating from benign (`$SI < $FN`) | Avoids the red herring |
| Resident `$DATA` in the `$MFT` | The flag lives inside the tampered record |

---

## Intended path

### 1. `$MFT` → find the lie
```
MFTECmd.exe -f "$MFT" --csv . --csvf mft.csv
```
Sort/scan `Created0x10` (`$SI`) vs `Created0x30` (`$FN`):

| File | `$SI` Created | `$FN` Created | Verdict |
|---|---|---|---|
| **customer_export.csv** | **2024-06-14 15:15:00** | **2026-08-27 21:34:30** | `$SI` backdated **2 years** — stomped |
| 7z-x64-installer.exe | 2026-07-10 16:00:00 | 2026-08-27 21:34:30 | `$SI < $FN` by *weeks* — **benign** (extracted installer keeps the archive's stored date) |
| readme.txt / notes.txt | 2026-08-27 … | 2026-08-27 … | normal |

The installer is the red herring: `$SI < $FN` is *normal* for files unzipped from an archive.
Only `customer_export.csv` was backdated by years — that is the tampering.

### 2. `$J` (USN journal) → the ground truth
```
MFTECmd.exe -f "$J" --csv . --csvf usn.csv
```
```
customer_export.csv  2026-08-27 21:34:30  FileCreate
customer_export.csv  2026-08-27 21:34:30  DataExtend|FileCreate|Close
```
The journal — which the operator did not scrub — records the file being **created on
2026-08-27**, flatly contradicting its `$SI` claim of 2024. And moments later:
```
WinTime.cs   2026-08-27 21:34:31  FileCreate     <- source of the timestomp tool
WinTime.exe  2026-08-27 21:34:32  FileCreate     <- compiled on the host, then run
```
The operator compiled a small `SetFileTime` utility on the box and ran it. `$MFT` shows both
still sitting in `C:\Users\bayrem\AppData\Local\Temp\`. (`Amcache.hve` is provided as the
application-inventory hive; the definitive tool evidence here is the `$J`+`$MFT` create sequence.)

### 3. Recover what was staged
`customer_export.csv` is only 223 bytes, so its `$DATA` is **resident inside its `$MFT`
record** — no disk image needed. Dump the resident data (MFTExplorer, or simply):
```
strings "$MFT" | grep Securinets
→ Securinets{si_backdated_fn_never_lies}
```
The flag string self-documents the whole lesson: `$SI` was backdated, but `$FN` never lies.

---

## Trick & red herring
- **Trick:** `$SI` can be forged, `$FN` cannot — and the USN journal is a second, independent
  witness. Detecting anti-forensics rather than recovering data.
- **Red herring:** `7z-x64-installer.exe` also has `$SI < $FN`, which a hasty analyst flags — but
  that pattern is *normal* for extracted archives (margin of weeks, and a plausible build date),
  versus the 2-year jump on the real target.

---

## Build notes (how it was made)

Built on `ctf-win` from `golden`, headless via `guestcontrol`; guest clock set to the incident
moment (`lab.ps1 date ctf-win 2026-08-27T14:30`, PST) so `$FN`/USN land on the breach day.

1. Staged the exfil files as `bayrem` at incident time (true `$SI`=`$FN`=2026-08-27 21:34 UTC).
2. Compiled `WinTime.exe` (a `File.SetCreationTime` stub) **in-guest** and ran it on
   `customer_export.csv` → `$SI` → 2024-06-14, `$FN` untouched. Red-herring installer given a
   weeks-old `$SI` to mimic archive extraction.
3. Ran the Compatibility Appraiser to refresh `Amcache.hve`.
4. **Acquisition is offline & contamination-free:** clean shutdown → `VBoxManage clonemedium`
   the merged disk to RAW → **TSK** (`icat`) extracted `$MFT` (inode 0), `$LogFile` (2),
   `$UsnJrnl:$J` (`49584-128-3`), `Amcache.hve` — so no extractor ever ran on the victim to
   pollute these very artifacts.
5. Verified: MFTECmd shows `$SI`≪`$FN` on the target and benign on the installer; USN confirms
   the true create time + the tool compilation; flag resident in `$MFT` (exactly one
   `Securinets{` hit); author-identity scrub clean.

**Design note:** the spec called for Amcache to carry the tool's SHA-1; a single manual appraiser
run did not inventory a fresh `%TEMP%` binary, so tool attribution is delivered (more concretely)
via the `$J`+`$MFT` create sequence, which shows the operator compiling `WinTime.cs`→`.exe` on
the host. `Amcache.hve` still ships (real, 103 entries) for authenticity.
