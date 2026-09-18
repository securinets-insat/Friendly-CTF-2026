#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#define ROUNDS 32
#define MAX_DATA 64

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
        random_state = (uint32_t)time(NULL) ^ (uint32_t)getpid() ^ 0x55504c44U;
    }
}

static void timed_out(int signal_number) {
    static const char message[] = "\nUPLOAD LOST\n";
    (void)signal_number;
    write(STDOUT_FILENO, message, sizeof(message) - 1);
    _exit(0);
}

static void put_u16(unsigned char *buffer, uint16_t value) {
    buffer[0] = (unsigned char)(value >> 8);
    buffer[1] = (unsigned char)value;
}

static void put_u32(unsigned char *buffer, uint32_t value) {
    buffer[0] = (unsigned char)(value >> 24);
    buffer[1] = (unsigned char)(value >> 16);
    buffer[2] = (unsigned char)(value >> 8);
    buffer[3] = (unsigned char)value;
}

static uint16_t get_u16(const unsigned char *buffer) {
    return (uint16_t)(((uint16_t)buffer[0] << 8) | buffer[1]);
}

static uint32_t get_u32(const unsigned char *buffer) {
    return ((uint32_t)buffer[0] << 24) | ((uint32_t)buffer[1] << 16) |
           ((uint32_t)buffer[2] << 8) | buffer[3];
}

static uint32_t checksum(const unsigned char *data, size_t length) {
    uint32_t total = 0;
    for (size_t index = 0; index < length; index++) {
        total += data[index];
    }
    return total;
}

static int read_exact(unsigned char *buffer, size_t length) {
    size_t received = 0;

    while (received < length) {
        ssize_t amount = read(STDIN_FILENO, buffer + received, length - received);
        if (amount <= 0) {
            return 0;
        }
        received += (size_t)amount;
    }
    return 1;
}

static void send_fragmented(const unsigned char *data, size_t length) {
    size_t sent = 0;

    while (sent < length) {
        size_t amount = 1 + (next_random() % 6);
        if (amount > length - sent) {
            amount = length - sent;
        }
        if (write(STDOUT_FILENO, data + sent, amount) <= 0) {
            _exit(0);
        }
        sent += amount;
        usleep(500);
    }
}

static int compare_bytes(const void *left, const void *right) {
    return *(const unsigned char *)left - *(const unsigned char *)right;
}

static size_t make_payload(unsigned char *payload, unsigned char operation) {
    size_t data_length = 24 + (next_random() % 24);
    unsigned char *data = payload;

    if (operation == 2 || operation == 3 || operation == 5) {
        payload[0] = (unsigned char)(1 + (next_random() % 255));
        data = payload + 1;
    }

    for (size_t index = 0; index < data_length; index++) {
        data[index] = (unsigned char)next_random();
    }

    data[0] = 0;
    data[1] = '\n';
    memcpy(data + 2, "LEEK", 4);

    if (operation == 3) {
        payload[0] = (unsigned char)(1 + (next_random() % (data_length - 1)));
    }

    return data_length + (data != payload);
}

static size_t solve_operation(unsigned char operation, const unsigned char *payload,
                              size_t payload_length, unsigned char *result) {
    const unsigned char *data = payload;
    size_t length = payload_length;
    unsigned char key = 0;

    if (operation == 2 || operation == 3 || operation == 5) {
        key = payload[0];
        data++;
        length--;
    }

    memcpy(result, data, length);

    if (operation == 1) {
        for (size_t left = 0, right = length - 1; left < right; left++, right--) {
            unsigned char temporary = result[left];
            result[left] = result[right];
            result[right] = temporary;
        }
    } else if (operation == 2) {
        for (size_t index = 0; index < length; index++) {
            result[index] ^= key;
        }
    } else if (operation == 3) {
        unsigned char temporary[MAX_DATA];
        size_t shift = key % length;
        memcpy(temporary, result + shift, length - shift);
        memcpy(temporary + length - shift, result, shift);
        memcpy(result, temporary, length);
    } else if (operation == 4) {
        qsort(result, length, 1, compare_bytes);
    } else {
        for (size_t index = 0; index < length; index++) {
            result[index] = (unsigned char)(result[index] + key);
        }
    }

    return length;
}

static void reveal_flag(void) {
    char flag[256];
    FILE *flag_file = fopen("flag.txt", "r");

    if (flag_file == NULL || fgets(flag, sizeof(flag), flag_file) == NULL) {
        puts("UPLOAD EMPTY");
        if (flag_file != NULL) {
            fclose(flag_file);
        }
        return;
    }

    fclose(flag_file);
    flag[strcspn(flag, "\r\n")] = '\0';
    puts("\nUPLOAD COMPLETE");
    puts(flag);
}

int main(void) {
    unsigned char payload[MAX_DATA];
    unsigned char expected[MAX_DATA];
    unsigned char answer[MAX_DATA];
    unsigned char frame[4 + 2 + 1 + 2 + MAX_DATA + 4];
    unsigned char reply_header[8];
    unsigned char reply_checksum[4];

    setvbuf(stdout, NULL, _IONBF, 0);
    signal(SIGALRM, timed_out);
    seed_random();

    puts("CYBERLEEK'S FINAL UPLOAD");
    puts("FRAME = LEEK | seq:u16 | op:u8 | len:u16 | payload | sum:u32");
    puts("REPLY = ACK! | seq:u16 | len:u16 | result | sum:u32");
    puts("All integers are big-endian. Sum means the sum of every byte.");
    puts("OPS: 1 REVERSE, 2 XOR, 3 ROTATE LEFT, 4 SORT, 5 ADD");
    puts("For XOR, ROTATE and ADD, payload[0] is the key and data follows.");
    puts("BEGIN UPLOAD");

    for (uint16_t sequence = 1; sequence <= ROUNDS; sequence++) {
        unsigned char operation = (unsigned char)(1 + (next_random() % 5));
        size_t payload_length = make_payload(payload, operation);
        size_t expected_length = solve_operation(operation, payload, payload_length, expected);

        memcpy(frame, "LEEK", 4);
        put_u16(frame + 4, sequence);
        frame[6] = operation;
        put_u16(frame + 7, (uint16_t)payload_length);
        memcpy(frame + 9, payload, payload_length);
        put_u32(frame + 9 + payload_length, checksum(payload, payload_length));

        printf("STATIC %08x\n", next_random());
        send_fragmented(frame, 9 + payload_length + 4);

        alarm(2);
        if (!read_exact(reply_header, sizeof(reply_header)) ||
            memcmp(reply_header, "ACK!", 4) != 0 ||
            get_u16(reply_header + 4) != sequence) {
            return 0;
        }

        size_t answer_length = get_u16(reply_header + 6);
        if (answer_length > MAX_DATA || !read_exact(answer, answer_length) ||
            !read_exact(reply_checksum, sizeof(reply_checksum))) {
            return 0;
        }
        alarm(0);

        if (answer_length != expected_length ||
            memcmp(answer, expected, expected_length) != 0 ||
            get_u32(reply_checksum) != checksum(answer, answer_length)) {
            puts("\nFRAME REJECTED");
            return 0;
        }

        puts("\nFRAME ACCEPTED");
    }

    reveal_flag();
    return 0;
}
