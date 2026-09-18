#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int fd;
int decode_index;
int bytes_read;
int received;
unsigned char unlock_key;
char flag[0x50];
char flag_path[] = {0x33, 0x39, 0x34, 0x32, 0x7b, 0x21, 0x2d, 0x21, 0x00};

void win(int arg1, int arg2, int arg3) {
    if (arg1 == 0x112233 && arg2 == 0x445566 && arg3 == 0x778899) {
        unlock_key = 0x55;

        for (decode_index = 0; decode_index < 8; decode_index++) {
            flag_path[decode_index] ^= unlock_key;
        }

        fd = open(flag_path, O_RDONLY);
        if (fd < 0) {
            exit(0);
        }

        bytes_read = (int)read(fd, flag, sizeof(flag));
        if (bytes_read > 0) {
            write(STDOUT_FILENO, flag, (size_t)bytes_read);
        }
        exit(0);
    }

    puts("ACCESS DENIED: intro detected");
    exit(0);
}

void setup(void) {
    setbuf(stdout, NULL);
    setbuf(stdin, NULL);
    setbuf(stderr, NULL);
}

void vuln(void) {
    char buffer[32];

    puts("SKIP INTRO");
    puts("Rockstar security is watching the beginning.");
    printf("SKIP: ");

    received = 0;
    while (received < 48) {
        bytes_read = (int)read(STDIN_FILENO, buffer + received, 48 - received);
        if (bytes_read <= 0) {
            exit(0);
        }
        received += bytes_read;
    }
}

int main(void) {
    setup();
    vuln();
    puts("The intro caught you.");
    return 0;
}
