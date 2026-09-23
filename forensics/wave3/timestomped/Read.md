# Timestomped

An internal host was staged for a data theft. Before exfil, the operator tried to hide the
staging folder in plain sight: every file in it looks like it has been sitting there for years.

The examiner pulled the NTFS metadata off the volume — nothing else. From these four files alone,
work out which item was tampered with, when it was *really* created, what tampered with it, and
recover what was staged.

**Artifacts**
- `$MFT` — Master File Table
- `$LogFile` — NTFS transaction log
- `$J` — the `$UsnJrnl:$J` change journal
- `Amcache.hve` — application execution/inventory hive
