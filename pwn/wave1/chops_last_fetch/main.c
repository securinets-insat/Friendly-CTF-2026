#include <ctype.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#define ROUNDS 45
#define VALUE_CAP 1024
#define COMMAND_CAP 128

static uint32_t rng_state;

static void answer_timeout(int signal_number) {
    static const char message[] = "\nChop got tired of waiting.\n";
    (void)signal_number;
    write(STDOUT_FILENO, message, sizeof(message) - 1);
    _exit(0);
}

static uint32_t next_random(void) {
    uint32_t x = rng_state;
    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;
    rng_state = x;
    return x;
}

static size_t random_below(size_t limit) {
    return limit == 0 ? 0 : (size_t)(next_random() % limit);
}

static void seed_random(void) {
    FILE *random_source = fopen("/dev/urandom", "rb");
    if (random_source != NULL) {
        if (fread(&rng_state, sizeof(rng_state), 1, random_source) != 1) {
            rng_state = 0;
        }
        fclose(random_source);
    }

    if (rng_state == 0) {
        rng_state = (uint32_t)time(NULL) ^ (uint32_t)getpid() ^ 0x43484f50U;
    }
}

static int compare_bytes(const void *left, const void *right) {
    return *(const unsigned char *)left - *(const unsigned char *)right;
}

static void reverse_value(char *value, size_t length) {
    for (size_t left = 0, right = length - 1; left < right; left++, right--) {
        char temporary = value[left];
        value[left] = value[right];
        value[right] = temporary;
    }
}

static void rotate_left(char *value, size_t length, size_t amount) {
    char temporary[VALUE_CAP];

    if (length < 2) {
        return;
    }

    amount %= length;
    memcpy(temporary, value + amount, length - amount);
    memcpy(temporary + length - amount, value, amount);
    memcpy(value, temporary, length);
}

static void append_command(char *command, const char *operation) {
    if (command[0] != '\0') {
        strncat(command, " | ", COMMAND_CAP - strlen(command) - 1);
    }
    strncat(command, operation, COMMAND_CAP - strlen(command) - 1);
}

static void apply_string_operation(char *value, char *command, int advanced) {
    char operation[32];
    size_t length = strlen(value);
    size_t choices = advanced ? 7 : 4;

    switch (random_below(choices)) {
        case 0:
            append_command(command, "REVERSE");
            reverse_value(value, length);
            break;
        case 1:
            append_command(command, "BARK");
            for (size_t index = 0; index < length; index++) {
                value[index] = (char)toupper((unsigned char)value[index]);
            }
            break;
        case 2:
            append_command(command, "WHISPER");
            for (size_t index = 0; index < length; index++) {
                value[index] = (char)tolower((unsigned char)value[index]);
            }
            break;
        case 3: {
            size_t repetitions = 2 + random_below(2);
            char original[VALUE_CAP];
            memcpy(original, value, length + 1);
            snprintf(operation, sizeof(operation), "REPEAT %zu", repetitions);
            append_command(command, operation);
            for (size_t count = 1; count < repetitions; count++) {
                memcpy(value + (count * length), original, length);
            }
            value[length * repetitions] = '\0';
            break;
        }
        case 4: {
            size_t amount = 1 + random_below(length - 1);
            snprintf(operation, sizeof(operation), "ROTATE %zu", amount);
            append_command(command, operation);
            rotate_left(value, length, amount);
            break;
        }
        case 5: {
            size_t start = random_below(length - 1);
            size_t end = start + 1 + random_below(length - start);
            snprintf(operation, sizeof(operation), "SLICE %zu %zu", start, end);
            append_command(command, operation);
            memmove(value, value + start, end - start);
            value[end - start] = '\0';
            break;
        }
        default:
            append_command(command, "SORT");
            qsort(value, length, 1, compare_bytes);
            break;
    }
}

static void build_round(char *package, char *expected, char *command, int round) {
    static const char *packages[] = {
        "ViceCity-map_v2",
        "Port Gellhorn cache",
        "Leonida Keys #6",
        "OceanDrive/NIGHT",
        "R* build: 2026",
        "NOOSE-route.alpha",
        "Blaine County tape",
        "Chop's red collar",
        "VEHICLE_LIST[07]",
        "mission=final_fetch",
        "PAYLOAD: not-a-prompt",
        "Gator Keys radio"
    };
    size_t package_count = sizeof(packages) / sizeof(packages[0]);

    snprintf(package, VALUE_CAP, "%s|%04u", packages[random_below(package_count)],
             (unsigned int)random_below(10000));
    memcpy(expected, package, strlen(package) + 1);
    command[0] = '\0';

    if (round < 10 && random_below(5) == 0) {
        append_command(command, "FETCH");
        return;
    }

    if (round < 10) {
        apply_string_operation(expected, command, 0);
        return;
    }

    if (round < 25) {
        size_t choice = random_below(10);
        if (choice < 7) {
            apply_string_operation(expected, command, 1);
        } else if (choice == 7) {
            char converted[VALUE_CAP];
            unsigned int key = 1U + (unsigned int)random_below(255);
            size_t length = strlen(expected);
            snprintf(command, COMMAND_CAP, "XOR %u", key);
            for (size_t index = 0; index < length; index++) {
                snprintf(converted + (index * 2), 3, "%02x",
                         ((unsigned char)expected[index]) ^ key);
            }
            memcpy(expected, converted, (length * 2) + 1);
        } else if (choice == 8) {
            snprintf(command, COMMAND_CAP, "COUNT");
            snprintf(expected, VALUE_CAP, "%zu", strlen(expected));
        } else {
            append_command(command, "FETCH");
        }
        return;
    }

    apply_string_operation(expected, command, 1);
    apply_string_operation(expected, command, 1);
}

static int receive_answer(char *answer, size_t capacity) {
    size_t length;

    if (fgets(answer, (int)capacity, stdin) == NULL) {
        return 0;
    }

    length = strlen(answer);
    while (length > 0 && (answer[length - 1] == '\n' || answer[length - 1] == '\r')) {
        answer[--length] = '\0';
    }
    return 1;
}

static void reveal_flag(void) {
    char flag[256];
    FILE *flag_file = fopen("flag.txt", "r");

    if (flag_file == NULL || fgets(flag, sizeof(flag), flag_file) == NULL) {
        puts("Chop returned empty-pawed.");
        if (flag_file != NULL) {
            fclose(flag_file);
        }
        return;
    }
    fclose(flag_file);
    flag[strcspn(flag, "\r\n")] = '\0';

    puts("\n          / \\__");
    puts("         (    @\\___");
    puts("         /         O");
    puts("        /   (_____/");
    puts("       /_____/   U");
    puts("\nCHOP'S LAST FETCH:");
    puts(flag);
}

int main(void) {
    static const char *radio_lines[] = {
        "Lamar: Chop caught another scent.",
        "CyberLeek: The courier signal just moved.",
        "Unknown: Another piece crossed the city.",
        "Lamar: Keep up. Chop does not wait.",
        "CyberLeek: The drop is still intact."
    };
    char package[VALUE_CAP];
    char expected[VALUE_CAP];
    char answer[VALUE_CAP];
    char command[COMMAND_CAP];

    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stdin, NULL, _IONBF, 0);
    signal(SIGALRM, answer_timeout);
    seed_random();

    puts("CHOP'S LAST FETCH");
    puts("The package length is exact. Commands run from left to right.");
    puts("ROTATE goes left. SLICE uses [start, end). XOR returns lowercase hex.\n");

    for (int round = 0; round < ROUNDS; round++) {
        build_round(package, expected, command, round);

        puts(radio_lines[random_below(sizeof(radio_lines) / sizeof(radio_lines[0]))]);
        printf("ROUND: %02d/%d\n", round + 1, ROUNDS);
        printf("COMMAND: %s\n", command);
        printf("PACKAGE SIZE: %zu\n", strlen(package));
        printf("PACKAGE: ");
        fwrite(package, 1, strlen(package), stdout);
        printf("\nCHOP RETURNS: ");

        alarm(2);
        if (!receive_answer(answer, sizeof(answer))) {
            return 0;
        }
        alarm(0);

        if (strcmp(answer, expected) != 0) {
            puts("Chop growls. Wrong handler.");
            return 0;
        }
        puts("Good boy.\n");
    }

    reveal_flag();
    return 0;
}
