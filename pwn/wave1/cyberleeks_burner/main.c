#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#define ROUNDS 8

static uint32_t random_state;

static uint32_t next_random(void) {
    uint32_t value = random_state;
    value ^= value << 13;
    value ^= value >> 17;
    value ^= value << 5;
    random_state = value;
    return value;
}

static void seed_random(void) {
    FILE *source = fopen("/dev/urandom", "rb");

    if (source != NULL) {
        if (fread(&random_state, sizeof(random_state), 1, source) != 1) {
            random_state = 0;
        }
        fclose(source);
    }

    if (random_state == 0) {
        random_state = (uint32_t)time(NULL) ^ (uint32_t)getpid() ^ 0x4c45454bU;
    }
}

static void answer_timeout(int signal_number) {
    static const char message[] = "\nThe burner disconnected.\n";
    (void)signal_number;
    write(STDOUT_FILENO, message, sizeof(message) - 1);
    _exit(0);
}

static int read_answer(char *answer, size_t size) {
    size_t length;

    if (fgets(answer, (int)size, stdin) == NULL) {
        return 0;
    }

    length = strlen(answer);
    while (length > 0 && (answer[length - 1] == '\n' || answer[length - 1] == '\r')) {
        answer[--length] = '\0';
    }
    return 1;
}

static void print_flag(void) {
    char flag[256];
    FILE *flag_file = fopen("flag.txt", "r");

    if (flag_file == NULL || fgets(flag, sizeof(flag), flag_file) == NULL) {
        puts("The burner is empty.");
        if (flag_file != NULL) {
            fclose(flag_file);
        }
        return;
    }

    fclose(flag_file);
    flag[strcspn(flag, "\r\n")] = '\0';

    puts(".--------------------.");
    puts("| CYBERLEEK  ONLINE  |");
    puts("|  BURNER UNLOCKED   |");
    puts("'--------------------'");
    puts("LEAK RECOVERED:");
    puts(flag);
}

int main(void) {
    static const char *leaks[] = {
        "vice_city_build",
        "leonida_map",
        "lucia_archive",
        "rockstar_vault",
        "port_gellhorn",
        "ocean_drive_cam",
        "mission_script",
        "vehicle_roster"
    };
    char transmission[128];
    char answer[128];

    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stdin, NULL, _IONBF, 0);
    signal(SIGALRM, answer_timeout);
    seed_random();

    puts("CYBERLEEK'S BURNER");
    puts("The line is live. Return every transmission intact.\n");

    for (int round = 0; round < ROUNDS; round++) {
        snprintf(transmission, sizeof(transmission), "%s_%08x",
                 leaks[next_random() % (sizeof(leaks) / sizeof(leaks[0]))],
                 next_random());

        printf("TRANSMISSION %d/%d\n", round + 1, ROUNDS);
        puts("BEGIN LEAK");
        puts(transmission);
        puts("END LEAK");
        printf("RETURN LEAK: ");

        alarm(2);
        if (!read_answer(answer, sizeof(answer))) {
            return 0;
        }
        alarm(0);

        if (strcmp(answer, transmission) != 0) {
            puts("Signal rejected.");
            return 0;
        }

        puts("Signal confirmed.\n");
    }

    print_flag();
    return 0;
}
