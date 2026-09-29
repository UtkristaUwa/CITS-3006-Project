# RE-02 — Obfuscated Secret Recovery

## Category
Reverse engineering

## Objective
Recover a hidden flag from a stripped executable whose flag and validation code
are stored only in transformed form.

## Vulnerability / Design
Both the accepted validation code and the flag are stored as byte arrays XOR-ed
with a **repeating multi-byte key**. There is no plaintext copy of either value,
and no plaintext string comparison — the accepted code is reconstructed at
runtime, so `strings` and a single-byte XOR guess both fail. The binary is
compiled stripped (`gcc -O2 -s`).

## Intended Techniques
- `strings` (confirm nothing sensitive leaks)
- disassembly / decompilation to locate `KEY`, `code_enc`, `flag_enc`
- data-flow analysis of the `xform` (repeating-key XOR) routine
- reproduce the transform to decode `flag_enc`

## Intended Solution
Locate the multi-byte `KEY` and the `flag_enc` array in the binary and XOR them
with the repeating key (`flag_enc[i] ^ KEY[i % len(KEY)]`) to recover the flag
directly — the validation gate is not required to reach it.

## Flag
CITS3006{RE02_XOR_DATAFLOW}

## Included Files
- `re02.c` — source
- `re02` — compiled, stripped binary (the challenge artifact)
