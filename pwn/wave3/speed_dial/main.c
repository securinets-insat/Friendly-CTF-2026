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
    open("flag",O_RDONLY);
    
}


void vuln(){
    char buf[0x200];
    int n = read(0,buf,sizeof(buf)-1);
    syscall(strlen(buf),n,buf,sizeof(buf)-1);
    puts(buf);
    return;
}

void main(){
    setup();
    vuln();
    exit(0);
}