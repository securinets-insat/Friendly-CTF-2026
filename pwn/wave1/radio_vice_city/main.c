#include <unistd.h>
#include<stdlib.h>
#include<stdio.h>
#include<string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>



void getTopSecretAssest(){
    int f = open("flag",O_RDONLY);
    char flag[0x50];
    read(f,flag,sizeof(flag));
    close(f);
    return;
}



void setup(){
    setbuf(stdout,0);
    setbuf(stdin,0);
    setbuf(stderr,0);
    
}


void vuln(){
    char buf[0x100];
    read(0,buf,sizeof(buf));
    printf(buf);
    return;
}

void f5(){
    char buf[67];
    vuln();
    return;
}
void f4(){
    char buf[50];
    f5();
}
void f3(){
    char buf[10];
    f4();
}
void f2(){
    char buf[0x200];
    f3();
}
void f1(){
    getTopSecretAssest();
    f2();
}

void challenge(){

    f1();

}

void main(){
    setup();
    challenge();
    exit(0);
}