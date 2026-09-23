# ADV-01 — AES-CTR Nonce Reuse

## Category
Advanced — Cryptographic vulnerability

## Objective
Recover the protected flag by exploiting reuse of an AES-CTR nonce.

## Vulnerability
The same AES-CTR key and nonce were reused for two different plaintext messages. CTR mode generates the same keystream when the key and nonce are reused, allowing the keystream to be recovered from known plaintext and used against another ciphertext.

## Intended Technique
1. Obtain the supplied known plaintext.
2. Obtain the known ciphertext and flag ciphertext.
3. Confirm that the same nonce was reused.
4. XOR the known plaintext with its ciphertext to recover the CTR keystream.
5. XOR the recovered keystream with the flag ciphertext.
6. Recover the ADV-01 flag.

## Flag
CITS3006{ADV01_AES_CTR_NONCE_REUSE}
