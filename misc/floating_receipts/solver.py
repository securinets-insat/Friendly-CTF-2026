#!/usr/bin/env python3

import struct


flag = b""
for line in open("receipts.txt"):
    flag += struct.pack("<f", float(line))

print(flag.rstrip(b"\0").decode())
