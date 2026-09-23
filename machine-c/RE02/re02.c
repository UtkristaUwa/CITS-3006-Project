#include <stdio.h>
#include <stdint.h>
#include <string.h>

static const uint8_t encoded[] = {
    0x18, 0x12, 0x0f, 0x08, 0x68, 0x6b, 0x6b, 0x6d, 0x20, 0x09, 0x1e, 0x6b, 0x69, 0x04, 0x03, 0x14, 0x09, 0x04, 0x1f, 0x1a, 0x0f, 0x1a, 0x1d, 0x17, 0x14, 0x0c, 0x26
};

static const uint8_t key = 0x5b;

static void decode(char *out, size_t n) {
    for (size_t i = 0; i < n; i++) {
        out[i] = (char)(encoded[i] ^ key);
    }
    out[n] = '\0';
}

int main(void) {
    char input[64];
    char secret[64];

    printf("=== CITS3006 Secure Validator ===\n");
    printf("Enter validation code: ");

    if (!fgets(input, sizeof(input), stdin)) {
        return 1;
    }

    input[strcspn(input, "\n")] = '\0';

    if (strcmp(input, "RE02-2026") == 0) {
        decode(secret, sizeof(encoded));
        printf("Validation accepted.\n");
        printf("Recovered token: %s\n", secret);
    } else {
        printf("Validation rejected.\n");
    }

    return 0;
}
