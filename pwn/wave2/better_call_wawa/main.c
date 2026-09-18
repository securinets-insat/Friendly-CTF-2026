#include <stdio.h>
#include <unistd.h>

void setup(void) {
    setbuf(stdout, NULL);
    setbuf(stdin, NULL);
    setbuf(stderr, NULL);
}

void answer_wawa(void) {
    char message[32];

    puts("BETTER CALL WAWA");
    puts("");
    puts("Some calls leave more than a voice behind.");
    printf("WAWA'S LINE: %p\n", (void *)stdout);
    puts("Leave your message:");
    read(STDIN_FILENO, message, 72);
}

int main(void) {
    setup();
    answer_wawa();
    puts("The line went silent.");
    return 0;
}
