#include <unistd.h>
#include<stdlib.h>
#include<stdio.h>
#include<string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>



void getTopSecretAssest(){
    int f = open("flag",O_RDONLY);
    char flag[0x100];
    read(f,flag,sizeof(flag));
    close(f);
    return;
}



void setup(){
    setbuf(stdout,0);
    setbuf(stdin,0);
    setbuf(stderr,0);
    
}




void challenge(){
    char buf[0x100];
    read(0,buf,sizeof(buf));
    printf(buf);
    return;
}


void main(){
    setup();
    getTopSecretAssest();
    challenge();
    exit(0);
}