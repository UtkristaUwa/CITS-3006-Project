#!/bin/bash
# CITS3006 VERT-02 provisioning — run as root on the target VM.
set -e

# low-privilege CTF user (foothold from an earlier stage lands here)
id ctfuser &>/dev/null || useradd -m -s /bin/bash ctfuser

# maintenance data the tool legitimately copies
mkdir -p /var/lib/ctf-maintenance
echo "system health: OK" > /var/lib/ctf-maintenance/report.txt

# the root-only flag
echo 'CITS3006{VERT02_PATH_HIJACK}' > /root/flag_vert02.txt
chmod 600 /root/flag_vert02.txt
chown root:root /root/flag_vert02.txt

# install the SUID-root maintenance binary
install -o root -g root -m 4755 ctf-maintenance /usr/local/bin/ctf-maintenance

echo "[+] VERT-02 provisioned. SUID binary at /usr/local/bin/ctf-maintenance"
