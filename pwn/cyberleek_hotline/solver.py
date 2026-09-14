#!/usr/bin/env python3
from pwn import *

context.log_level = "error"

p = process("./main") if args.LOCAL else remote("127.0.0.1", 9016)
print(p.recvall().decode())
p.close()
