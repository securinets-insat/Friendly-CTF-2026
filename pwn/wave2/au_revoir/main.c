#include <stdio.h>      // printf
#include <stdlib.h>
#include <netinet/in.h> // sockaddr_in, INADDR_ANY
#include <sys/socket.h> // socket, bind, listen, accept, AF_INET, SOCK_STREAM
#include <sys/types.h>  // htonl, htons, socklen_t
#include <unistd.h>     // read, write, close
#include <time.h>
#include <string.h>
#include <fcntl.h>


int client_fd = -1;


void win(int client_fd){
    puts("b");
    char flag[0x100];
    int fd = open("flag.txt",O_RDONLY);
    read(fd,flag,sizeof(flag)-2);
    close(fd);
    send(client_fd,flag, strlen(flag), 0);
}


void gadget(){
    __asm__("pop %rdi;ret;");
}


void setup(){
    setbuf(stdout,0);
    setbuf(stdin,0); 
    setbuf(stderr,0);
}


void vuln(){
    int server_fd = socket(AF_INET,SOCK_STREAM,0);
    if (server_fd == -1) {
        perror("socket");
        exit(-1);
    }
    struct sockaddr_in addr;
    addr.sin_family = AF_INET;
    addr.sin_port = htons(5000);
    addr.sin_addr.s_addr = INADDR_ANY;
    int opt = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    if(bind(server_fd,(struct sockaddr*) &addr,sizeof(addr))!=0){
        perror("Binding error");
        exit(-1);
    }
    if(listen(server_fd,5)!=0){
        perror("Listening error");
        exit(-1);
    }
    while(1){
        puts("Waiting...");
        int client_fd = accept(server_fd,NULL,NULL);

        if (client_fd == -1) {
            perror("accept");
            close(server_fd);
            exit(-1);
        }
        pid_t p=fork();
        if(p==0){
            for(;;){
                char wlc[0x100];
                sprintf(wlc,"Bonjour %d\n",client_fd);
                send(client_fd,wlc, strlen(wlc), 0);
                char buf[0x100];
                if(read(client_fd,buf,0x300)<0) {
                    send(client_fd, "Au revoir VYHVF\n", strlen("Au revoir VYHVF\n"), 0);
                    break;
                }
            }
            close(client_fd);
            close(server_fd);
            return;
        }
        close(client_fd);
    }
    close(server_fd);
    return;
}
void main(){
    setup();
    vuln();
    return;
}

