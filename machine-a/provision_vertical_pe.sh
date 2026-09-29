#!/usr/bin/env bash
#
# provision_vertical_pe.sh — Machine A (vertical privilege escalation)
# CITS3006 CTF project — Meridian Robotics Dev Portal
#
# Run as root, AFTER provision_horizontal_pe.sh (depends on `build` and
# /srv/build already existing).
#
# Vuln: `build` (from horizontal PE) can already read
# /srv/build/backups/pre-audit-2026-07-09/, which holds a "pre-audit backup"
# of sysadmin's home dir — their encrypted SSH key plus the key passphrase,
# which is NOT in the clear: it is protected by the ADV AES-CTR challenge
# (audit_capture.txt) whose key+nonce were reused, so it is recoverable.
# sysadmin has no password (key-only, sudo NOPASSWD), so that archive — once
# the passphrase is broken — is the only way in. See the Exploit Report doc.
#
set -euo pipefail

if [[ $EUID -ne 0 ]]; then
  echo "Run this as root." >&2
  exit 1
fi

if ! id build &>/dev/null || [[ ! -d /srv/build ]]; then
  echo "This depends on provision_horizontal_pe.sh already having run" >&2
  echo "(needs the 'build' user and /srv/build to exist). Run that first." >&2
  exit 1
fi

SYSADMIN_USER="sysadmin"
SYSADMIN_PASSPHRASE="M3ridian_D3v!"
BACKUP_DIR="/srv/build/backups/pre-audit-2026-07-09"

echo "[*] Creating user ${SYSADMIN_USER} with sudo rights"
if ! id "${SYSADMIN_USER}" &>/dev/null; then
  useradd -m -s /bin/bash "${SYSADMIN_USER}"
fi
usermod -aG sudo "${SYSADMIN_USER}"
passwd -l "${SYSADMIN_USER}" >/dev/null   # key-only account, no password auth

# NOPASSWD: the locked password above means a normal password-prompting
# sudo rule can never succeed for this user -- the key is its only credential.
echo "${SYSADMIN_USER} ALL=(ALL) NOPASSWD: ALL" > "/etc/sudoers.d/${SYSADMIN_USER}"
chmod 440 "/etc/sudoers.d/${SYSADMIN_USER}"

echo "[*] Generating sysadmin's encrypted SSH keypair"
SYSADMIN_HOME="/home/${SYSADMIN_USER}"
mkdir -p "${SYSADMIN_HOME}/.ssh"
KEY_TMP=$(mktemp -d)
ssh-keygen -t ed25519 -N "${SYSADMIN_PASSPHRASE}" -C "sysadmin@meridian-robotics" \
  -f "${KEY_TMP}/id_ed25519" >/dev/null

cat "${KEY_TMP}/id_ed25519.pub" >> "${SYSADMIN_HOME}/.ssh/authorized_keys"
chown -R "${SYSADMIN_USER}:${SYSADMIN_USER}" "${SYSADMIN_HOME}/.ssh"
chmod 700 "${SYSADMIN_HOME}/.ssh"
chmod 600 "${SYSADMIN_HOME}/.ssh/authorized_keys"

echo "[*] Building the pre-audit backup (the actual vertical PE artifact)"
mkdir -p "${BACKUP_DIR}"

# Decoys: real tar.gz files for the other users, nothing sensitive inside.
for u in jchen mfoster; do
  D=$(mktemp -d)
  mkdir -p "${D}/${u}_home"
  cat > "${D}/${u}_home/notes.txt" <<EOF
Home directory backup -- ${u}
Pre-audit sweep, 2026-07-09. Nothing else of note here.
EOF
  tar -czf "${BACKUP_DIR}/${u}_home.tar.gz" -C "${D}" "${u}_home"
  rm -rf "${D}"
done

# The real one: sysadmin's home backup, including the encrypted key.
D=$(mktemp -d)
mkdir -p "${D}/sysadmin_home/.ssh"
cp "${KEY_TMP}/id_ed25519" "${D}/sysadmin_home/.ssh/id_ed25519"
cp "${KEY_TMP}/id_ed25519.pub" "${D}/sysadmin_home/.ssh/id_ed25519.pub"
cat > "${D}/sysadmin_home/backup_notes.txt" <<'EOF'
Pre-audit sweep 2026-07-09. Backed up jchen/mfoster/sysadmin home dirs
per checklist item 4.2 ahead of the Q3 audit.

NOTE: not writing sysadmin's key passphrase here in the clear this time
(last audit flagged exactly that). It was run through the ops audit-encryption
tool together with the routine audit log -- both are in audit_capture.txt in
this archive, and audit_record_sample.txt is the plaintext of the audit log.
The tool reused the same audit key + nonce for both records again, though.

-- ops_svc
EOF

# --- Chain link: fold in the ADV (AES-CTR) capture so the passphrase is
# recoverable ONLY by breaking the reused key/nonce. audit_record_sample.txt
# is the known plaintext; audit_capture.txt holds both ciphertexts. ---
ADV_DIR="$(dirname "$0")/ADV_aes-ctr"
if [[ ! -f "${ADV_DIR}/challenge.txt" || ! -f "${ADV_DIR}/known_plaintext.txt" ]]; then
  echo "Missing ADV_aes-ctr capture files next to this script." >&2
  exit 1
fi
cp "${ADV_DIR}/challenge.txt"       "${D}/sysadmin_home/audit_capture.txt"
cp "${ADV_DIR}/known_plaintext.txt" "${D}/sysadmin_home/audit_record_sample.txt"
tar -czf "${BACKUP_DIR}/sysadmin_home.tar.gz" -C "${D}" "sysadmin_home"
rm -rf "${D}" "${KEY_TMP}"

chown -R build:build /srv/build/backups
find /srv/build/backups -type d -exec chmod 755 {} \;
find /srv/build/backups -type f -exec chmod 644 {} \;

echo "[*] Planting the flag (root-only)"
echo "FLAG{PE_V3rt1c4l_H4S_b3En_D0N3}" > /root/flag_vertical.txt
chmod 600 /root/flag_vertical.txt

echo "[*] Sanity checks"
if sudo -l -U "${SYSADMIN_USER}" 2>&1 | grep -qi "may run"; then
  echo "  OK: sysadmin has sudo rights."
else
  echo "  !!! WARNING: sysadmin sudo rights not detected -- check manually."
fi
if sudo -l -U build 2>&1 | grep -qi "not allowed"; then
  echo "  OK: build still has no sudo rights."
else
  echo "  !!! WARNING: build may have picked up sudo -- investigate."
fi
if sudo -l -U ops_svc 2>&1 | grep -qi "not allowed"; then
  echo "  OK: ops_svc still has no sudo rights."
else
  echo "  !!! WARNING: ops_svc may have picked up sudo -- investigate."
fi

cat <<EOF

Done.

  - sysadmin login is key-only. The encrypted key comes from the backup, but
    the passphrase is NO LONGER in the clear -- it must be recovered by solving
    the AES-CTR nonce reuse in audit_capture.txt (ADV challenge). Builder ref:
    the passphrase is ${SYSADMIN_PASSPHRASE} and the ADV flag falls out with it.
  - sudo for sysadmin is NOPASSWD (locked password can't back a prompt).
  - Flag: /root/flag_vertical.txt, root-only, readable via 'sudo cat'.
EOF
