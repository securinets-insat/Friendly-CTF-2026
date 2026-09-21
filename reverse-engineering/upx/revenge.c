#include <stdio.h>
#include <string.h>

unsigned char data[] = {
    0x1e, 0x2a, 0x29, 0x3a, 0x3f, 0x26, 0x24, 0x2a,
    0x39, 0x3c, 0x31, 0x1b, 0x79, 0x03, 0x0b, 0x7c,
    0x12, 0x16, 0x7e, 0x10, 0x1f, 0x7b, 0x02, 0x02,
    0x7d, 0x1a, 0x04, 0x7e, 0x12, 0x7c, 0x06, 0x10,
    0x18, 0x1f, 0x12, 0x10, 0x01, 0x09, 0x7a, 0x1a,
    0x18, 0x1a, 0x73, 0x10, 0x19, 0x7b, 0x06, 0x0e,
    0x7e, 0x32, 0x00
};

unsigned char key[] = {
    'M', 'O', 'J', 'O'
};

int main() {

    char input[128];

    printf("========================================\n");
    printf("              REVENGE\n");
    printf("========================================\n");
    printf("\n");
    printf("The flag is not where you think it is.\n");
    printf("Something is hiding behind the layers...\n");
    printf("\n");

    printf("Enter the flag: ");
    scanf("%127s", input);

    
    int length = sizeof(data) - 1;

    for (int i = 0; i < length; i++) {
        data[i] ^= key[i % 4];
    }

    if (strcmp(input, (char *)data) == 0) {
        printf("\n");
        printf("Correct!\n");
        printf("You broke through the encryption.\n");
    } else {
        printf("\n");
        printf("Wrong flag.\n");
    }

    return 0;
}
