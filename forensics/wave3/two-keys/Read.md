# Two Keys

EDR flagged a workstation, but by the time anyone looked the process was already gone from disk.
All that was captured is a full **RAM image**. One suspicious process is still resident.

Reverse it and recover the secret — which comes in **two halves, recovered two different ways**.
Concatenate them in order: `Securinets{<A>_<B>}`.

**File:** `mem.raw.zst` (zstd-compressed VirtualBox memory image)

Hint: one half is *executed* in emulation, the other you have to *run for yourself*.
