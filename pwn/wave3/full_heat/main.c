#include <stdio.h>
#include <unistd.h>

typedef struct {
    long reserved;
    const char *message;
    int (*send)(const char *);
} Broadcast;

static int reports;

void scramble(char *report) {
    int i = 0;

    while (report[i]) {
        dprintf(1, "%c", (unsigned char)report[i] ^ 0x5a);
        i++;
    }

    dprintf(1, "\n");
}

void wanted_report(void) {
    char report[40];

    reports++;

    dprintf(1, "FULL HEAT RESPONSE TERMINAL\n"
               "WANTED LEVEL: FIVE STARS\n"
               "How did CyberLeek enter Leonida?\n> ");
    read(0, report, 0x40);

    if (reports < 3) {
        dprintf(1, "Rockstar archived:\n");
        scramble(report);
    } else {
        dprintf(1, "Rockstar archived the report.\n");
    }

    dprintf(1, "Correct the report before we lock the city:\n> ");
    read(0, report, reports == 1 ? 0x39 : 0x68);
}

void broadcast(Broadcast alert) {
    alert.send(alert.message);
}

int main(void) {
    puts("ROCKSTAR INCIDENT NETWORK");

    if (reports)
        return 0;

    fflush(NULL);
    wanted_report();
}
