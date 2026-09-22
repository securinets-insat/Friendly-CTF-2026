#include <unistd.h>
#include <string.h>
#include <seccomp.h>
#include <sys/prctl.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <sys/mman.h>
#define _GNU_SOURCE


void win(){
    system("/bin/sh");
}

void setup(){
    setbuf(stdout,0);
    setbuf(stdin,0); 
    setbuf(stderr,0);
}
void vuln(){
    char * p;
    char buf[0x20];
    p=buf;
    char ** p2=&p;
    long long i = 0x67;
    for(int j =0;j<=1;j++){
    read(0,buf,0x20);
    printf(buf);}
    if (i==0xc0) win();
    return;
}
void main(){
    setup();
    vuln();
    return;
}

