#include <stdio.h>
#include <stdint.h>
#include <string.h>

static const uint8_t expected_code[] = {
    0xfd, 0xe9, 0xc6, 0xd6, 0xfa, 0x98, 0x88, 0x94
};

static const uint8_t encoded_flag[] = {
    0x2e, 0x2f, 0x4f, 0x5f, 0x8a, 0x94, 0x9f, 0xa8, 0x6e, 0xa2, 0x96, 0xd6, 0xe2, 0xc1, 0xd3, 0xe4, 0xdc, 0xde, 0x04, 0xfc, 0xfe, 0x26, 0x12, 0x25, 0x31, 0x45, 0x4c, 0x4e, 0x5c, 0x6d, 0x70, 0x65
};

static int validate(const char *input) {
    size_t len = strlen(input);

    if (len != sizeof(expected_code)) {
        return 0;
    }

    for (size_t i = 0; i < sizeof(expected_code); i++) {
        uint8_t x = (uint8_t)input[i];

        x ^= 0x37;
        x = (uint8_t)(x + (uint8_t)(i * 7));
        x ^= 0xa5;

        if (x != expected_code[i]) {
            return 0;
        }
    }

    return 1;
}

static void reveal_flag(void) {
    char flag[sizeof(encoded_flag) + 1];

    for (size_t i = 0; i < sizeof(encoded_flag); i++) {
        uint8_t x = encoded_flag[i];

        x = (uint8_t)(x - (uint8_t)(i * 11));
        x ^= 0x6d;

        flag[i] = (char)x;
    }

    flag[sizeof(encoded_flag)] = '\0';

    printf("Recovered flag: %s\n", flag);
}

int main(void) {
    char input[64];

    printf("=== CITS3006 Integrity Validator ===\n");
    printf("Enter validation code: ");

    if (!fgets(input, sizeof(input), stdin)) {
        return 1;
    }

    input[strcspn(input, "\n")] = '\0';

    if (validate(input)) {
        puts("Validation accepted.");
        reveal_flag();
    } else {
        puts("Validation rejected.");
    }

    return 0;
}
