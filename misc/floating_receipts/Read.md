# FLOATING RECEIPTS

## Challenge

The player receives `receipts.txt`, containing a short list of unusual decimal
floating-point values.

## Solution

The values are not measurements. Every value is a four-byte IEEE-754 `float32`
whose raw little-endian bytes are four consecutive flag characters.

Parse every line as a number, pack it back into a little-endian float, join the
resulting bytes, and remove the null padding at the end.

```bash
python3 solver.py
```

Output:

```text
Securinets{y3s_th3s3_fl04ts_4r3_t0t4lly_l3g1t_r3c31pts_trust_m3}
```

Run `python3 make.py` to rebuild the attachment after changing the flag.
