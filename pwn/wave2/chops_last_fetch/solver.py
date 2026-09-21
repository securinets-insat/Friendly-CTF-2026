#!/usr/bin/env python3
from pwn import *

context.log_level = "error"


def solve_command(data, command):
    commands = command.split(b" | ")

    for current in commands:
        words = current.split()

        if words[0] == b"FETCH":
            pass
        elif words[0] == b"REVERSE":
            data = data[::-1]
        elif words[0] == b"BARK":
            data = data.upper()
        elif words[0] == b"WHISPER":
            data = data.lower()
        elif words[0] == b"REPEAT":
            data = data * int(words[1])
        elif words[0] == b"ROTATE":
            amount = int(words[1])
            data = data[amount:] + data[:amount]
        elif words[0] == b"SLICE":
            start = int(words[1])
            end = int(words[2])
            data = data[start:end]
        elif words[0] == b"SORT":
            data = bytes(sorted(data))
        elif words[0] == b"XOR":
            key = int(words[1])
            data = bytes(byte ^ key for byte in data).hex().encode()
        elif words[0] == b"COUNT":
            data = str(len(data)).encode()

    return data


io = remote("127.0.0.1", 9003)

for _ in range(45):
    io.recvuntil(b"COMMAND: ")
    command = io.recvline().strip()

    io.recvuntil(b"PACKAGE SIZE: ")
    package_size = int(io.recvline())

    io.recvuntil(b"PACKAGE: ")
    package = io.recvn(package_size)

    answer = solve_command(package, command)
    io.sendlineafter(b"CHOP RETURNS: ", answer)

io.recvuntil(b"CHOP'S LAST FETCH:\n")
flag = io.recvline().decode().strip()
print(flag)
io.close()
