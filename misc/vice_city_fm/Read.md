# VICE CITY FM

## Challenge

The player receives `playlist.m3u`. The audio files are missing, but every
playlist entry still contains an unusual duration.

## Solution

M3U metadata stores a track duration after `#EXTINF:`. In this playlist, every
duration is the decimal ASCII value of one flag character.

For example:

```text
#EXTINF:83,Vice City Track 00
```

The duration `83` is ASCII `S`. Extract every duration in order and convert the
numbers to bytes.

```bash
python3 solver.py
```

Output:

```text
Securinets{th3_pl4yl1st_w4s_th3_l34k}
```

Run `python3 make.py` whenever the flag changes.
