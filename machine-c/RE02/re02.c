#include <stdio.h>
#include <stdint.h>
#include <string.h>

/* CITS3006 RE-02 — Obfuscated Secret Recovery
 * The validation code and the flag are stored only in transformed form.
 * A repeating multi-byte key is applied per byte; there is no plaintext
 * copy of either the accepted code or the flag anywhere in the binary.
 */

static const uint8_t KEY[8] = { 0x9e, 0x37, 0xc1, 0x6b, 0x4a, 0xf5, 0x28, 0xb3 };
static const uint8_t code_enc[16] = { 0xcb, 0x79, 0x8d, 0x24, 0x09, 0xbe, 0x05, 0x80, 0xae, 0x07, 0xf7, 0x46, 0x07, 0xb0, 0x7c, 0xf2 };
static const uint8_t flag_enc[27] = { 0xdd, 0x7e, 0x95, 0x38, 0x79, 0xc5, 0x18, 0x85, 0xe5, 0x65, 0x84, 0x5b, 0x78, 0xaa, 0x70, 0xfc, 0xcc, 0x68, 0x85, 0x2a, 0x1e, 0xb4, 0x6e, 0xff, 0xd1, 0x60, 0xbc };

static void xform(const uint8_t *in, size_t n, char *out) {
    for (size_t i = 0; i < n; i++)
        out[i] = (char)(in[i] ^ KEY[i % sizeof(KEY)]);
    out[n] = '\0';
}

int main(void) {
    char input[128];
    char code[sizeof(code_enc) + 1];
    char flag[sizeof(flag_enc) + 1];

    printf("=== CITS3006 Secure Validator ===\n");
    printf("Enter validation code: ");
    if (!fgets(input, sizeof(input), stdin)) return 1;
    input[strcspn(input, "\n")] = '\0';

    /* decode the accepted code at runtime and compare — no plaintext gate */
    xform(code_enc, sizeof(code_enc), code);

    if (strcmp(input, code) == 0) {
        xform(flag_enc, sizeof(flag_enc), flag);
        printf("Validation accepted.\n");
        printf("Recovered token: %s\n", flag);
    } else {
        printf("Validation rejected.\n");
    }
    return 0;
}
