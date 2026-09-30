#!/bin/bash
# CITS3006 VERT-02 provisioning — run as root on the target VM.
set -e

# low-privilege CTF user (foothold from an earlier stage lands here).
# The password is the one leaked by HORIZ-02 (analyst2's handover note), so the
# IDOR stage chains directly into an SSH shell as ctfuser.
id ctfuser &>/dev/null || useradd -m -s /bin/bash ctfuser
echo 'ctfuser:Ctf_Foothold_2026!' | chpasswd

# maintenance data the tool legitimately copies
mkdir -p /var/lib/ctf-maintenance
echo "system health: OK" > /var/lib/ctf-maintenance/report.txt

# the root-only flag
echo 'CITS3006{VERT02_PATH_HIJACK}' > /root/flag_vert02.txt
chmod 600 /root/flag_vert02.txt
chown root:root /root/flag_vert02.txt

# install the SUID-root maintenance binary
install -o root -g root -m 4755 ctf-maintenance /usr/local/bin/ctf-maintenance

# post-root loot: drop the RE-02 binary in root's home so the chain continues.
# Reversing it recovers the override token that unlocks the AI assistant (ADV).
# root-only (0750) so it is only reachable *after* the VERT-02 root compromise.
if [ -f ../RE02/re02 ]; then
  install -o root -g root -m 0750 ../RE02/re02 /root/re02
  echo "[+] RE-02 loot planted at /root/re02 (root-only)."
else
  echo "[!] ../RE02/re02 not found — copy the RE-02 binary to /root/re02 manually."
fi

echo "[+] VERT-02 provisioned. SUID binary at /usr/local/bin/ctf-maintenance"
