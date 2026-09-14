#include <stdio.h>

int main(void) {
    char flag[128];
    FILE *file;

    setbuf(stdout, NULL);

    puts("CYBERLEEK HOTLINE");
    puts("Connection accepted. Cyberleek is sending the package...");

    file = fopen("flag.txt", "r");
    if (!file)
        return 1;

    fgets(flag, sizeof(flag), file);
    fclose(file);

    puts(flag);
    return 0;
}
