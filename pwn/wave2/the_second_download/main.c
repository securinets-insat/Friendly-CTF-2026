#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <unistd.h>

#define PAGE_SIZE 0x1000
#define FIRST_FRAGMENT 4

typedef void (*upload_t)(int, void *, size_t);

int read_exact(void *buffer, size_t length) {
    size_t received = 0;

    while (received < length) {
        ssize_t amount = read(STDIN_FILENO, (char *)buffer + received,
                              length - received);

        if (amount <= 0) {
            return 0;
        }

        received += (size_t)amount;
    }

    return 1;
}

int main(void) {
    void *upload;

    setbuf(stdout, NULL);
    setbuf(stdin, NULL);
    setbuf(stderr, NULL);

    upload = mmap(NULL, PAGE_SIZE, PROT_READ | PROT_WRITE | PROT_EXEC,
                  MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);

    if (upload == MAP_FAILED) {
        return 0;
    }

    puts("THE SECOND DOWNLOAD");
    puts("Rockstar accepted the beginning of the transfer.");
    printf("FIRST FRAGMENT: ");

    if (!read_exact(upload, FIRST_FRAGMENT)) {
        return 0;
    }

    ((upload_t)upload)(STDIN_FILENO, upload, PAGE_SIZE);
    return 0;
}
