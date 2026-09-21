/* compile: gcc -o main main.c -lseccomp  -Wl,-z,relro,-z,now -pie -no-pie -fno-stack-protector
no pie,full relro,no canary
ret2shellcode
flag path should be sth unknown / random idk 
*/ 
#include <unistd.h>
#include <string.h>
#include <seccomp.h>
#include <sys/prctl.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <sys/mman.h>
#define _GNU_SOURCE



void setup(){
    mmap(
        (void*)0x67676767000,
        0x1000,
        PROT_READ | PROT_WRITE | PROT_EXEC,
        MAP_PRIVATE | MAP_ANONYMOUS | MAP_FIXED,
        -1,
        0
    ); 
    setbuf(stdout,0);
    setbuf(stdin,0); 
    setbuf(stderr,0);
}

void vuln(){
    char buf[0x200];
    read(0,buf,0x220);
    printf(buf);
    return;
}
void main(){
    setup();
    vuln();
    return;
}

