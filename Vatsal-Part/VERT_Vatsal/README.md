# VERT-03 — SUID Shared-Library Hijacking

## Category
Vertical privilege escalation

## Objective
Escalate to root by exploiting an SUID executable that loads a shared library from a writable directory.

## Intended Technique
1. Identify the SUID-root executable.
2. Determine the shared library search path.
3. Identify that the library directory is writable.
4. Replace the legitimate library with a controlled library.
5. Execute the SUID program.
6. Obtain root privileges.
7. Recover the VERT-03 flag.

## Included Files
- ctf-vert03
- lib/libctfhelper.so

The supplied library is the legitimate clean library. The malicious library used during exploitation is not included.
