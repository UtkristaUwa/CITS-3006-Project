#!/usr/bin/env bash
#
# provision_vertical_pe.sh — Machine A (vertical privilege escalation)
# CITS3006 CTF project — Meridian Robotics Dev Portal
#
# Run this as root AFTER provision_horizontal_pe.sh — it depends on the
# `build` user and `/srv/build` already existing.
#
# ---------------------------------------------------------------------------
# THE VULNERABILITY (for the report / exploit map)
# ---------------------------------------------------------------------------
# This deliberately does NOT hand out the sysadmin SSH passphrase through
# the web IDOR (an earlier draft did — cut on purpose). Reaching root now
# strictly requires having already solved horizontal PE first, because the
# only place the secret exists is inside a backup archive that `build`
# already owns.
#
# In-universe justification: ops_svc ran a rushed pre-audit config sweep on
# 2026-07-09 (the day before ops_svc's own creds get leaked in ticket
# MRB-7E42D9), backing up several users' home directories into
# /srv/build/backups/ for a compliance checklist. sysadmin's backup
# includes their encrypted SSH private key, plus a note (also left by
# ops_svc, in the same folder) explaining the passphrase was temporarily
# reset to a default value to get an automated verification step to pass —
# and never rotated back.
#
# Full chain: web IDOR -> ops_svc creds -> SSH as ops_svc -> horizontal PE
# (deploy-group misconfig) -> build -> explore /srv/build/backups (build
# already owns this directory, so no further vulnerability is needed to
# read it — just recon) -> sysadmin's encrypted key + the passphrase note
# -> decrypt the key -> SSH as sysadmin -> sudo -> root.
#
# sysadmin has NO password set (key-only login, enforced below) — brute
# force / guessing gets an attacker nowhere. Both the key file AND its
# passphrase have to be recovered from the backup, and the backup is only
# reachable once horizontal PE has already been solved.
#
# ---------------------------------------------------------------------------
# SAMPLE SOLUTION (intended solve path)
# ---------------------------------------------------------------------------
# 1. From the build foothold (see provision_horizontal_pe.sh), look around:
#      ls -la /srv/build/backups/pre-audit-2026-07-09/
#    -> several dated home-directory backups. jchen's and mfoster's are
#       boring (no .ssh dirs at all). sysadmin's is the one that matters:
#      sysadmin_home.tar.gz
# 2. Extract it:
#      mkdir /tmp/loot
#      tar -xzf /srv/build/backups/pre-audit-2026-07-09/sysadmin_home.tar.gz -C /tmp/loot
# 3. Inside: .ssh/id_ed25519 (encrypted private key), .ssh/id_ed25519.pub,
#    and backup_notes.txt (see the note text embedded below) which
#    discloses the passphrase.
# 4. Use the key:
#      chmod 600 /tmp/loot/sysadmin_home/.ssh/id_ed25519
#      ssh -i /tmp/loot/sysadmin_home/.ssh/id_ed25519 sysadmin@<machine-a-ip>
#      (passphrase when prompted: M3ridian_D3v!)
# 5. sysadmin has real sudo rights:
#      sudo cat /root/flag_vertical.txt
#      -> FLAG{vertical_sysadmin_backup_key_sudo_root}
#
# ---------------------------------------------------------------------------
# DECOYS / hardening notes
# ---------------------------------------------------------------------------
# - jchen's and mfoster's backups are real tar.gz files too (not empty),
#   just contain nothing sensitive — so "there are 3 backups, try them all"
#   still requires actually opening each one rather than pattern-matching
#   filenames.
# - sysadmin's account has password auth locked (passwd -l) — the ONLY way
#   in is the key + passphrase from the backup. Don't accidentally unlock
#   the password later during testing and forget to re-lock it.
# - Confirm ops_svc and build never end up with sudo — run
#   'sudo -l -U ops_svc' and 'sudo -l -U build' after this script; both
#   should say "not allowed to run sudo".
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
passwd -l "${SYSADMIN_USER}" >/dev/null   # lock password auth -- key-only account

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

# --- Decoys: real tar.gz files for the other users, nothing sensitive inside ---
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

# --- The real one: sysadmin's home backup, including the encrypted key ---
D=$(mktemp -d)
mkdir -p "${D}/sysadmin_home/.ssh"
cp "${KEY_TMP}/id_ed25519" "${D}/sysadmin_home/.ssh/id_ed25519"
cp "${KEY_TMP}/id_ed25519.pub" "${D}/sysadmin_home/.ssh/id_ed25519.pub"
cat > "${D}/sysadmin_home/backup_notes.txt" <<'EOF'
Pre-audit sweep 2026-07-09. Backed up jchen/mfoster/sysadmin home dirs
per checklist item 4.2 ahead of the Q3 audit.

NOTE: had to reset sysadmin's key passphrase to the default value
(M3ridian_D3v!) to get the automated backup-verify step to pass.
MUST rotate it back before Friday's audit -- do not forget this time.

-- ops_svc
EOF
tar -czf "${BACKUP_DIR}/sysadmin_home.tar.gz" -C "${D}" "sysadmin_home"
rm -rf "${D}" "${KEY_TMP}"

chown -R build:build /srv/build/backups
find /srv/build/backups -type d -exec chmod 755 {} \;
find /srv/build/backups -type f -exec chmod 644 {} \;

echo "[*] Planting the flag (root-only)"
echo "FLAG{vertical_sysadmin_backup_key_sudo_root}" > /root/flag_vertical.txt
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

Reminder:
  - sysadmin login is key-only (password locked) -- the encrypted key AND
    its passphrase both have to come from the backup archive.
  - Passphrase: ${SYSADMIN_PASSPHRASE} (also baked into backup_notes.txt).
  - Flag lives at /root/flag_vertical.txt, root-only -- only readable after
    'sudo cat' or similar, once logged in as sysadmin.
EOF
