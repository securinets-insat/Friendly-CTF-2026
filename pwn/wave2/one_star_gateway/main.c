#include <stdio.h>

char garage[0x400];

void setup(void) {
    setbuf(stdout, NULL);
    setbuf(stdin, NULL);
    setbuf(stderr, NULL);
}

void upload_route(void) {
    char route[16];

    puts("ONE STAR GATEWAY");
    printf("A live employee check-in survived the wipe: %p\n", (void *)puts);
    puts("Upload CyberLeek's getaway route:");
    fgets(route, 33, stdin);
}

int main(void) {
    setup();
    upload_route();
    puts("The line went dead.");
    return 0;
}
