/*
 * Meridian Robotics -- Firmware Diagnostic Utility v2.1
 *
 * Internal ops/build tool. Engineers: if you've lost your unlock code,
 * contact the build team -- do not brute-force this over a live serial
 * link, it locks the rig for 10 minutes.
 *
 * CITS3006 CTF project -- Machine A, reverse-engineering vulnerability.
 * This source file is NOT shipped on the box -- only the compiled,
 * stripped binary is (see provision_re.sh). Keep this .c file in the repo
 * for the report/exploit map, never on the VM itself.
 */
#include <stdio.h>
#include <string.h>

static const unsigned char key[] = {0x4d, 0x65, 0x72, 0x69, 0x64, 0x69, 0x61, 0x6e}; /* "Meridian" */
static const unsigned char enc_code[] = {0x1f, 0x55, 0x10, 0x59, 0x10, 0x58, 0x02, 0x1d, 0x60, 0x20, 0x1c, 0x0e, 0x49, 0x5e, 0x56, 0x5d, 0x79};
static const unsigned char enc_flag[] = {0x0b, 0x29, 0x33, 0x2e, 0x1f, 0x1b, 0x04, 0x31, 0x35, 0x0a, 0x00, 0x36, 0x11, 0x07, 0x0d, 0x01, 0x2e, 0x0e, 0x2d, 0x04, 0x01, 0x1b, 0x08, 0x0a, 0x24, 0x04, 0x1c, 0x36, 0x00, 0x00, 0x00, 0x09, 0x30};

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
