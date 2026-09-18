#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define RED   "\033[1;38;2;255;70;70m"
#define GREEN "\033[1;38;2;80;230;120m"
#define CYAN  "\033[1;38;2;60;210;255m"
#define GOLD  "\033[1;38;2;255;200;70m"
#define WHITE "\033[1;38;2;235;235;235m"
#define RESET "\033[0m"

struct wanted_record {
    char alias[32];
    char stars[4];
    unsigned int visible;
    unsigned int identified;
    unsigned int inside_area;
};

void setup(void) {
    setbuf(stdout, NULL);
    setbuf(stdin, NULL);
    setbuf(stderr, NULL);
}

void show_record(struct wanted_record *record, const char *title) {
    char alias[33];
    char stars[5];

    for (int i = 0; i < 32; i++) {
        unsigned char byte = record->alias[i];
        alias[i] = byte >= 0x20 && byte <= 0x7e ? byte : '.';
    }
    alias[32] = '\0';

    for (int i = 0; i < 4; i++) {
        unsigned char byte = record->stars[i];
        stars[i] = byte >= 0x20 && byte <= 0x7e ? byte : '.';
    }
    stars[4] = '\0';

    printf("\n" GOLD "%s" RESET "\n", title);
    printf("Record begins at: %p\n\n", (void *)record);
    printf(GOLD "OFFSET   FIELD          CURRENT                          REQUIRED\n" RESET);

    printf(CYAN "+0x00    alias[32]      %-32.32s anything\n" RESET,
           alias);

    printf("%s+0x20    stars          %-32.4s NONE%s\n",
           memcmp(record->stars, "NONE", 4) == 0 ? GREEN : RED,
           stars, RESET);

    printf("%s+0x24    visible        %-32u 0%s\n",
           record->visible == 0 ? GREEN : RED,
           record->visible, RESET);

    printf("%s+0x28    identified     %-32u 0%s\n",
           record->identified == 0 ? GREEN : RED,
           record->identified, RESET);

    printf("%s+0x2c    inside_area    %-32u 0%s\n",
           record->inside_area == 0 ? GREEN : RED,
           record->inside_area, RESET);
}

void release_archive(void) {
    char flag[128];
    FILE *file = fopen("flag.txt", "r");

    if (!file)
        exit(0);

    fgets(flag, sizeof(flag), file);
    fclose(file);

    puts(GREEN "\nPROFILE UPDATED");
    puts("WANTED LEVEL CLEARED");
    puts("ARCHIVE ACCESS GRANTED" RESET);
    puts(flag);
}

void update_record(void) {
    struct wanted_record record = {
        "CYBERLEEK",
        "RED ",
        1,
        1,
        1
    };

    puts("OFF THE RADAR");
    puts("ROCKSTAR WANTED NETWORK");
    puts("SUBJECT: CYBERLEEK");

    show_record(&record, "RECORD MEMORY BEFORE UPDATE");

    puts("\nRegister a new driver alias:");
    read(STDIN_FILENO, record.alias, sizeof(record));

    show_record(&record, "RECORD MEMORY AFTER UPDATE");

    if (memcmp(record.stars, "NONE", 4) == 0 &&
        record.visible == 0 &&
        record.identified == 0 &&
        record.inside_area == 0) {
        release_archive();
        return;
    }

    puts(RED "\nThe patrol still has your trail." RESET);
    puts("The alias occupies 32 bytes. Inspect what follows it.");
}

int main(void) {
    setup();
    update_record();
    return 0;
}
