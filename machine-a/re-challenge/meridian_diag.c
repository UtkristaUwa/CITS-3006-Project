/*
 * Meridian Robotics -- Firmware Diagnostic Utility v2.1
 *
 * CITS3006 CTF project -- Machine A, reverse-engineering vulnerability.
 * Source only, never shipped on the VM -- provision_re.sh compiles it fresh
 * (stripped, no debug symbols).
 */
#include <stdio.h>
#include <string.h>

static const unsigned char key[] = {0x4d, 0x65, 0x72, 0x69, 0x64, 0x69, 0x61, 0x6e}; /* "Meridian" */
static const unsigned char enc_code[] = {0x1f, 0x55, 0x10, 0x59, 0x10, 0x58, 0x02, 0x1d, 0x60, 0x20, 0x1c, 0x0e, 0x49, 0x5e, 0x56, 0x5d, 0x79};
static const unsigned char enc_flag[] = {0x0e, 0x2c, 0x26, 0x3a, 0x57, 0x59, 0x51, 0x58, 0x36, 0x17, 0x17, 0x36, 0x1c, 0x06, 0x13, 0x31, 0x38, 0x0b, 0x1e, 0x06, 0x07, 0x02, 0x3e, 0x03, 0x28, 0x17, 0x1b, 0x0d, 0x0d, 0x08, 0x0f, 0x31, 0x29, 0x0c, 0x13, 0x0e, 0x19};

int main(void) {
    char input[64];

    printf("Meridian Robotics -- Firmware Diagnostic Utility v2.1\n");
    printf("Enter engineer unlock code: ");
    fflush(stdout);

    if (!fgets(input, sizeof(input), stdin)) {
        return 1;
    }
    input[strcspn(input, "\n")] = '\0';

    size_t len = strlen(input);
    if (len != sizeof(enc_code)) {
        printf("Access denied.\n");
        return 1;
    }

    for (size_t i = 0; i < len; i++) {
        unsigned char c = (unsigned char)input[i] ^ key[i % sizeof(key)];
        if (c != enc_code[i]) {
            printf("Access denied.\n");
            return 1;
        }
    }

    printf("Unlock accepted. Diagnostic mode enabled.\n");
    for (size_t i = 0; i < sizeof(enc_flag); i++) {
        putchar(enc_flag[i] ^ key[i % sizeof(key)]);
    }
    putchar('\n');
    return 0;
}
