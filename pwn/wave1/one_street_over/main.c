#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

void enter_the_safehouse(void);

void receive_route(char *route) {
    size_t received = 0;

    while (received < 41) {
        ssize_t amount = read(STDIN_FILENO, route + received, 41 - received);

        if (amount <= 0) {
            exit(0);
        }

        received += (size_t)amount;
    }
}

void follow_the_route(void) {
    char route[32];

    puts("The getaway route is already locked.");
    printf("FINAL TURN: ");
    receive_route(route);
}

__attribute__((aligned(256)))
int main(void) {
    setbuf(stdout, NULL);
    setbuf(stdin, NULL);
    setbuf(stderr, NULL);

    puts("ONE STREET OVER");
    follow_the_route();
    puts("CyberLeek returned empty-handed.");
    return 0;
}

void enter_the_safehouse(void) {
    char flag[128];
    int file;
    ssize_t length;

    file = open("flag.txt", O_RDONLY);
    if (file < 0) {
        _exit(0);
    }

    length = read(file, flag, sizeof(flag));
    if (length > 0) {
        write(STDOUT_FILENO, "HANDOFF COMPLETE\n", 17);
        write(STDOUT_FILENO, flag, (size_t)length);
    }

    _exit(0);
}
