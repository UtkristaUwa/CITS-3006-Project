# RE-03 — Transformed Validation

## Category
Reverse engineering

## Objective
Recover a hidden flag by reversing a compiled validation routine and reconstructing its transformation logic.

## Challenge
The expected validation code and flag are stored as transformed byte arrays. The program applies per-byte arithmetic and XOR operations before comparing input or reconstructing the flag.

## Intended Techniques
- strings
- symbol inspection
- disassembly
- control-flow analysis
- data-flow analysis
- byte-level transformation analysis

## Flag
CITS3006{RE03_TRANSFORMED_CHECK}
