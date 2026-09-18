#!/usr/bin/env python3
from pwn import *

io = remote(args.HOST or "localhost", int(args.PORT or 9001))
io.sendline(b"cat flag.txt")
io.interactive()
