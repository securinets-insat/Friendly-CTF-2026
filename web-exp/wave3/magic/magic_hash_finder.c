// magic_hash_finder.c
// Multi-threaded brute-force search for "magic hash" style digests:
// hex digests matching ^0e[0-9]+$ (PHP loose-comparison / type-juggling bug).
//
// Build:
//   gcc -O3 -march=native -pthread magic_hash_finder.c -o magic_hash_finder -lssl -lcrypto
//
// Run:
//   ./magic_hash_finder <algo: md5|sha1|sha256> <start> <end> <num_threads>
// Example:
//   ./magic_hash_finder sha1 0 1000000000000 8

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <pthread.h>
#include <openssl/md5.h>
#include <openssl/sha.h>

typedef struct {
    long long start;
    long long end;
    int thread_id;
    char algo[16];
    volatile int *found_flag;
} thread_args_t;

// Check if hex digest matches ^0e[0-9]+$
static int is_magic(const unsigned char *digest, int len) {
    char hex[65];
    for (int i = 0; i < len; i++) sprintf(hex + i*2, "%02x", digest[i]);
    hex[len*2] = '\0';

    if (hex[0] != '0' || hex[1] != 'e') return 0;
    for (int i = 2; i < len*2; i++) {
        if (hex[i] < '0' || hex[i] > '9') return 0;
    }
    return 1;
}

void *worker(void *arg) {
    thread_args_t *t = (thread_args_t *)arg;
    char buf[32];
    unsigned char digest[SHA256_DIGEST_LENGTH];
    int dlen = 0;

    for (long long i = t->start; i < t->end; i++) {
        if (*(t->found_flag)) return NULL;

        int len = snprintf(buf, sizeof(buf), "%lld", i);

        if (strcmp(t->algo, "md5") == 0) {
            MD5((unsigned char *)buf, len, digest);
            dlen = MD5_DIGEST_LENGTH;
        } else if (strcmp(t->algo, "sha1") == 0) {
            SHA1((unsigned char *)buf, len, digest);
            dlen = SHA_DIGEST_LENGTH;
        } else if (strcmp(t->algo, "sha256") == 0) {
            SHA256((unsigned char *)buf, len, digest);
            dlen = SHA256_DIGEST_LENGTH;
        }

        if (is_magic(digest, dlen)) {
            char hex[65];
            for (int j = 0; j < dlen; j++) sprintf(hex + j*2, "%02x", digest[j]);
            hex[dlen*2] = '\0';
            printf("[thread %d] FOUND: input=%s  hash=%s\n", t->thread_id, buf, hex);
            *(t->found_flag) = 1;
            return NULL;
        }

        if (i % 200000000 == 0 && i != t->start) {
            printf("[thread %d] progress: %lld\n", t->thread_id, i);
        }
    }
    return NULL;
}

int main(int argc, char **argv) {
    if (argc != 5) {
        fprintf(stderr, "Usage: %s <md5|sha1|sha256> <start> <end> <num_threads>\n", argv[0]);
        return 1;
    }

    char *algo = argv[1];
    long long start = atoll(argv[2]);
    long long end = atoll(argv[3]);
    int nthreads = atoi(argv[4]);

    pthread_t threads[nthreads];
    thread_args_t targs[nthreads];
    volatile int found_flag = 0;

    long long range = end - start;
    long long chunk = range / nthreads;

    printf("Searching %s magic hashes over [%lld, %lld) with %d threads...\n",
           algo, start, end, nthreads);

    for (int i = 0; i < nthreads; i++) {
        targs[i].start = start + i * chunk;
        targs[i].end = (i == nthreads - 1) ? end : start + (i + 1) * chunk;
        targs[i].thread_id = i;
        targs[i].found_flag = &found_flag;
        strncpy(targs[i].algo, algo, sizeof(targs[i].algo));
        pthread_create(&threads[i], NULL, worker, &targs[i]);
    }

    for (int i = 0; i < nthreads; i++) {
        pthread_join(threads[i], NULL);
    }

    if (!found_flag) {
        printf("No match found in range [%lld, %lld)\n", start, end);
    }

    return 0;
}