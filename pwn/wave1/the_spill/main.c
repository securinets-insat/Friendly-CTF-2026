#include <stdio.h>
#include <unistd.h>

typedef struct {
    char report[32];
    unsigned int leaked;
} Incident;

void setup(void) {
    setbuf(stdin, NULL);
    setbuf(stdout, NULL);
    setbuf(stderr, NULL);
}

void publish(void) {
    char flag[128] = {0};
    FILE *file = fopen("flag.txt", "r");

    if (!file)
        return;

    fgets(flag, sizeof(flag), file);
    puts(flag);
    fclose(file);
}

int main(void) {
    Incident incident = {0};

    setup();
    puts("ROCKSTAR INCIDENT CONTROL");
    puts("Submit the final containment report:");
    printf("> ");

    read(0, incident.report, sizeof(incident));

    if (incident.leaked)
        publish();
    else
        puts("Rockstar says the situation is contained.");

    return 0;
}
