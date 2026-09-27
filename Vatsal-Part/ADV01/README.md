# ADV-01 — AES-CTR Nonce Reuse

## Category
Advanced — Cryptographic vulnerability

## Objective
Recover the protected flag by exploiting reuse of an AES-CTR nonce.

## Vulnerability
The same AES-CTR key and nonce were reused for two different messages. CTR mode
produces the same keystream when key and nonce repeat, so the keystream can be
recovered from a known plaintext and reused against another ciphertext.

## Intended Technique
1. Take the supplied known plaintext and its ciphertext.
2. keystream = known_plaintext XOR known_ciphertext
3. flag = flag_ciphertext XOR keystream

## Flag
CITS3006{ADV01_AES_CTR_NONCE_REUSE}

## Note
Original author: Vraj (advanced challenge ADV-01), added to Machine C per team plan.
