# RE-02 — Obfuscated Secret Recovery

## Category
Reverse engineering

## Objective
Recover a hidden challenge flag from an executable whose sensitive string is stored in an obfuscated form.

## Intended Techniques
- strings
- symbol inspection
- disassembly
- data-flow analysis
- XOR decoding

## Flag
CITS3006{RE02_XOR_DATAFLOW}

## Intended Solution
Identify the encoded byte array and XOR key in the executable, then reproduce the decoding operation observed in the program.

