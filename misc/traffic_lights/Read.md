# TRAFFIC LIGHTS

## Challenge

The player receives `traffic.txt`, containing a long sequence of colored
traffic-light emojis.

## Solution

The signals encode binary data:

- `🔴` is `0`;
- `🟢` is `1`;
- `🟡` separates bytes.

For example, the first group is:

```text
🔴 🟢 🔴 🟢 🔴 🔴 🟢 🟢 🟡
```

That becomes `01010011`, which is decimal `83` and ASCII `S`. Decode every
group in order to recover the flag.

```bash
python3 solver.py
```

Output:

```text
Securinets{r3d_gr33n_l1ghts_sp3ll_th3_l34k}
```

Run `python3 make.py` whenever the flag changes.
