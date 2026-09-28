# VERT-01 — SUID PATH Hijacking

## Category
Vertical privilege escalation

## Objective
Escalate from a low-privileged user to root by exploiting an insecure command-search path used by a SUID-root executable.

## Intended Technique
1. Identify the SUID-root executable.
2. Inspect its behaviour and command dependencies.
3. Identify the insecure PATH-based command execution.
4. Supply a controlled replacement executable.
5. Execute the SUID program.
6. Obtain root privileges and recover the VERT-01 flag.

## Included Files
- ctf-maintenance
