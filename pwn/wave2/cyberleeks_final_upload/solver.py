#!/usr/bin/env python3
from pwn import *

context.log_level = "error"

io = remote("127.0.0.1", 9004)
io.recvuntil(b"BEGIN UPLOAD\n")

for _ in range(32):
    io.recvuntil(b"LEEK")

    sequence = u16(io.recvn(2), endian="big")
    operation = io.recvn(1)[0]
    length = u16(io.recvn(2), endian="big")
    payload = io.recvn(length)
    received_sum = u32(io.recvn(4), endian="big")

    assert received_sum == sum(payload) & 0xffffffff

    data = payload
    if operation in (2, 3, 5):
        key = payload[0]
        data = payload[1:]

    if operation == 1:
        result = data[::-1]
    elif operation == 2:
        result = bytes(byte ^ key for byte in data)
    elif operation == 3:
        shift = key % len(data)
        result = data[shift:] + data[:shift]
    elif operation == 4:
        result = bytes(sorted(data))
    else:
        result = bytes((byte + key) & 0xff for byte in data)

    reply = b"ACK!"
    reply += p16(sequence, endian="big")
    reply += p16(len(result), endian="big")
    reply += result
    reply += p32(sum(result) & 0xffffffff, endian="big")
    io.send(reply)

io.recvuntil(b"UPLOAD COMPLETE\n")
print(io.recvline().decode().strip())
io.close()
