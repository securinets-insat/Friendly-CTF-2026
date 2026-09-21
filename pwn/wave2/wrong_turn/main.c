#include <unistd.h>
#include <string.h>
#include <seccomp.h>
#include <sys/prctl.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <sys/mman.h>
#define _GNU_SOURCE


void gadgets(){
    __asm__("jmp %rsi;");
}

void setup(){
    setbuf(stdout,0);
    setbuf(stdin,0); 
    setbuf(stderr,0);
}
void vuln(){
    char buf[0x200];
    read(0,buf,0x220);
    return;
}
void main(){
    setup();
    vuln();
    return;
}

