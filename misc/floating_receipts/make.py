#!/usr/bin/env python3

from pathlib import Path
import struct


flag = b"Securinets{y3s_th3s3_fl04ts_4r3_t0t4lly_l3g1t_r3c31pts_trust_m3}"
flag += b"\0" * (-len(flag) % 4)

numbers = []
for offset in range(0, len(flag), 4):
    value = struct.unpack("<f", flag[offset:offset + 4])[0]
    numbers.append(format(value, ".9g"))

Path(__file__).with_name("receipts.txt").write_text(
    "\n".join(numbers) + "\n", encoding="ascii"
)
