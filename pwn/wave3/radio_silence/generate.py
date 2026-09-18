#!/usr/bin/env python3

COUNT = 65536

header = r'''#include <ctype.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define FREQUENCY_COUNT 65536
#define TARGET_TAG 0x30db734fU
#define TARGET_CLEARANCE 0x2121796c6767696aULL

char radio_packet[512];
unsigned int active_frequency;

struct channel_frame {
    char code[16];
    uint64_t clearance;
};

char *gets(char *buffer);
void __stack_chk_fail(void);

void setup(void) {
    setbuf(stdout, NULL);
    setbuf(stdin, NULL);
    setbuf(stderr, NULL);
}

uint32_t route_tag(uint32_t value) {
    value ^= value >> 16;
    value *= 0x7feb352dU;
    value ^= value >> 15;
    value *= 0x846ca68bU;
    value ^= value >> 16;
    return value;
}

unsigned int protocol_for(unsigned int frequency) {
    return (frequency ^ (frequency >> 8) ^ 0x50U) & 3U;
}

uint64_t issue_clearance(unsigned int frequency) {
    uint64_t value = frequency + 0x9e3779b97f4a7c15ULL;
    unsigned int shift;
    unsigned char blocker;

    value = (value ^ (value >> 30)) * 0xbf58476d1ce4e5b9ULL;
    value = (value ^ (value >> 27)) * 0x94d049bb133111ebULL;
    value ^= value >> 31;

    if (route_tag(frequency) == TARGET_TAG)
        return TARGET_CLEARANCE;

    switch (protocol_for(frequency)) {
    case 0:
    case 1:
        blocker = '\n';
        break;
    case 2:
        blocker = ' ';
        break;
    default:
        blocker = '\0';
    }

    shift = ((frequency >> 3) & 7U) * 8U;
    value &= ~(0xffULL << shift);
    value |= (uint64_t)blocker << shift;
    return value;
}

void verify_clearance(volatile struct channel_frame *frame) {
    if (frame->clearance != issue_clearance(active_frequency))
        __stack_chk_fail();
}

__attribute__((noinline))
void line_zero(unsigned int frequency) {
    volatile struct channel_frame frame;
    active_frequency = frequency;
    frame.clearance = issue_clearance(frequency);
    gets((char *)frame.code);
    verify_clearance(&frame);
}

__attribute__((noinline))
void line_one(unsigned int frequency) {
    volatile struct channel_frame frame;
    active_frequency = frequency;
    frame.clearance = issue_clearance(frequency);
    fgets((char *)frame.code, 512, stdin);
    verify_clearance(&frame);
}

__attribute__((noinline))
void line_two(unsigned int frequency) {
    volatile struct channel_frame frame;
    active_frequency = frequency;
    frame.clearance = issue_clearance(frequency);
    scanf("%511s", (char *)frame.code);
    verify_clearance(&frame);
}

__attribute__((noinline))
void line_three(unsigned int frequency) {
    volatile struct channel_frame frame;
    active_frequency = frequency;
    frame.clearance = issue_clearance(frequency);
    fgets(radio_packet, sizeof(radio_packet), stdin);
    strcpy((char *)frame.code, radio_packet);
    verify_clearance(&frame);
}

'''

footer_start = r'''
void (*const frequency_table[FREQUENCY_COUNT])(void) = {
'''

footer_end = r'''
};

int valid_route(const char *route) {
    for (int i = 0; route[i]; i++) {
        if (isdigit((unsigned char)route[i]) ||
            isspace((unsigned char)route[i]) ||
            route[i] == '%' || route[i] == '$' || route[i] == 'p')
            continue;
        return 0;
    }
    return 1;
}

int main(void) {
    char route[32];
    long frequency;

    setup();

    puts("RADIO SILENCE");
    puts("Rockstar Emergency Broadcast Network");
    puts("\nTune to a frequency:");
    printf("> ");

    if (!fgets(route, sizeof(route), stdin) || !valid_route(route)) {
        puts("Signal rejected.");
        return 0;
    }

    puts("\nENCRYPTED ROUTE ECHO:");
    printf(route,
           (void *)0, (void *)0, (void *)0, (void *)0, (void *)0,
           (void *)0, (void *)0, (void *)0, (void *)0, (void *)0,
           (void *)0, (void *)0, (void *)0, (void *)0, (void *)0,
           (void *)0, (void *)0, (void *)0, (void *)0, (void *)0,
           (void *)0, (void *)0, (void *)0, (void *)0, (void *)0,
           (void *)0, (void *)0, (void *)0, (void *)0, (void *)0,
           (void *)0, (void *)0, (void *)0, (void *)0, (void *)0,
           (void *)0, (void *)0, (void *)0, (void *)0, (void *)0,
           (void *)puts);

    frequency = strtol(route, NULL, 10);
    if (frequency < 0 || frequency >= FREQUENCY_COUNT) {
        puts("Frequency outside Leonida.");
        return 0;
    }

    puts("\nFrequency accepted.");
    puts("Transmit clearance:");
    printf("> ");

    frequency_table[frequency]();
    puts("Transmission closed.");
    return 0;
}
'''

with open("main.c", "w") as source:
    source.write(header)

    for frequency in range(COUNT):
        protocol = (frequency ^ (frequency >> 8) ^ 0x50) & 3
        source.write(
            f"__attribute__((noinline, used)) "
            f"void frequency_{frequency}(void) "
            f"{{ line_{['zero', 'one', 'two', 'three'][protocol]}"
            f"({frequency}U); }}\n"
        )

    source.write(footer_start)

    for frequency in range(COUNT):
        source.write(f"    frequency_{frequency},\n")

    source.write(footer_end)
