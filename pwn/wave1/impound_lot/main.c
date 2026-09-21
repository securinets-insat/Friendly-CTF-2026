#include <stdio.h>

typedef struct {
    char cars[3][32];
    char secret[64];
} Archive;

int main(void) {
    Archive archive = {.cars = {"Banshee", "Cheetah", "Buffalo"}};
    char choice[8];
    unsigned int slot;
    FILE *file;

    setbuf(stdout, NULL);
    file = fopen("flag.txt", "r");
    if (!file) return 1;
    fgets(archive.secret, sizeof(archive.secret), file);
    fclose(file);

    puts("ROCKSTAR IMPOUND LOT");
    printf("Choose vehicle slot [0-2]: ");
    if (!fgets(choice, sizeof(choice), stdin)) return 1;
    slot = (unsigned int)(choice[0] - '0');
    puts(archive.cars[slot]);
    return 0;
}
