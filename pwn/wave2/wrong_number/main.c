#include <unistd.h>
#include<stdlib.h>
#include<stdio.h>
#include<string.h>
#include <fcntl.h>
#include <sys/syscall.h>




void setup(){
    setbuf(stdout,0);
    setbuf(stdin,0);
    setbuf(stderr,0);
    
}


void vuln(){
    char buf[0x200];
    int n = read(0,buf,sizeof(buf)-1);
    syscall(n,0,"/bin/sh",NULL,NULL);
    return;
}

void main(){
    setup();
    vuln();
    exit(0);
}