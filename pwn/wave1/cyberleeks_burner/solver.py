#!/usr/bin/env python3
from pwn import *

context.log_level = "error"

io = remote("127.0.0.1", 9002)

for _ in range(8):
    io.recvuntil(b"BEGIN LEAK\n")
    leak = io.recvline().strip()
    io.sendlineafter(b"RETURN LEAK: ", leak)

io.recvuntil(b"LEAK RECOVERED:\n")
print(io.recvline().decode().strip())
io.close()
