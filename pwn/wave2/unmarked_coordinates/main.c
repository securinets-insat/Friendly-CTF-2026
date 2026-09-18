#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define LUCIA 0x4c55434941c35fULL
#define JASON 0x4a41534f4ec35eULL
#define CHOP  0x43484f50c35aULL

void complete_the_handoff(uint64_t lucia, uint64_t jason, uint64_t chop) {
    char flag[128];
    char route[9];
    FILE *file;
    uint64_t access;
    uint64_t route_code;

    access = (lucia == LUCIA) & (jason == JASON) & (chop == CHOP);
    route_code = 0x70616d2e74736f6cULL;
    route_code ^= (0ULL - access) & 0x041919001312030aULL;

    memcpy(route, &route_code, 8);
    route[8] = '\0';

    file = fopen(route, "r");
    if (file == NULL) {
        puts("The crew was refused.");
        exit(0);
    }

    fgets(flag, sizeof(flag), file);
    fclose(file);

    puts("HANDOFF COMPLETE");
    puts(flag);
    exit(0);
}

void leonida_relay(void) {
    printf("SIGNAL: %p\n", (void *)leonida_relay);
}

void answer_the_burner(void) {
    char message[32];

    puts("The coordinates arrived without a label.");
    printf("MESSAGE: ");
    read(STDIN_FILENO, message, 200);
}

int main(void) {
    setbuf(stdout, NULL);
    setbuf(stdin, NULL);
    setbuf(stderr, NULL);

    puts("UNMARKED COORDINATES");
    leonida_relay();
    answer_the_burner();
    puts("The signal disappeared.");
    return 0;
}
