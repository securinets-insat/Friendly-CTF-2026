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
    puts("Let's see the diff between printf and puts");
    read(0,buf,sizeof(buf)-1);
    if(strlen(buf)>5) exit(0);
    sprintf(buf,"Your text : %s ",buf);
    printf(buf);
    puts(buf);
    return;
}

void main(){
    setup();
    vuln();
    exit(0);
}