#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

__attribute__((force_align_arg_pointer))
void steal_build(void) {
    char flag[128];
    FILE *file = fopen("flag.txt", "r");

    if (!file) exit(1);
    fgets(flag, sizeof(flag), file);
    fclose(file);
    puts(flag);
    exit(0);
}

int main(void) {
    char route[24];

    setbuf(stdout, NULL);
    puts("BACKSEAT DRIVER");
    puts("Enter CyberLeek's escape route:");
    read(STDIN_FILENO, route, 64);
    puts("Wrong turn.");
    return 0;
}
