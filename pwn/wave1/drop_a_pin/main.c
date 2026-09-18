#include <stdio.h>
#include <stdlib.h>

void setup(void) {
    setbuf(stdout, NULL);
    setbuf(stdin, NULL);
    setbuf(stderr, NULL);
}

void final_upload(void) {
    char flag[128];
    FILE *file = fopen("flag.txt", "r");

    if (!file)
        exit(0);

    fgets(flag, sizeof(flag), file);
    fclose(file);

    puts("\nRoute accepted.");
    puts("Opening CyberLeek's upload...");
    puts(flag);
}

int main(void) {
    unsigned long address;
    void (*destination)(void);

    setup();

    puts("DROP A PIN");
    puts("Rockstar Secure Navigation");
    puts("\nEnter the crew's destination:");
    printf("> ");

    if (scanf("%lx", &address) != 1) {
        puts("That is not a location.");
        return 0;
    }

    destination = (void (*)(void))address;

    if (destination != final_upload) {
        puts("Wrong street. The driver left without you.");
        return 0;
    }

    destination();
    return 0;
}
