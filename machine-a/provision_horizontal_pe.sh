#!/usr/bin/env bash
#
# provision_horizontal_pe.sh — Machine A (horizontal privilege escalation)
# CITS3006 CTF project — Meridian Robotics Dev Portal
#
# Run this ONCE, as root, directly on the real Machine A VM (not on your dev
# machine, not in a container simulation) after the base OS is installed and
# before the box ships to the shared CTF network. This is deliberately
# OS-level (real users, real groups, real file permissions) rather than
# another Flask/Python service, since horizontal PE only makes sense against
# a real multi-user box.
#
# ---------------------------------------------------------------------------
# THE VULNERABILITY (for the report / exploit map)
# ---------------------------------------------------------------------------
# An attacker who already has ops_svc's credentials — leaked via the web
# IDOR, ticket MRB-7E42D9 ("Rotate ops_svc credentials before audit") —
# can SSH in as ops_svc. From there they can reach a second, same-privilege
# service account (`build`) because ops_svc is a leftover member of the
# `deploy` group.
#
# In-universe justification: ticket MRB-1A2B3C ("Staging build pipeline
# failing... permissions error writing to /srv/build") is jchen's very
# first ticket, filed months before the game's "present". The lore is that
# sysadmin temporarily added ops_svc to the `deploy` group while debugging
# that Jenkins permissions issue, fixed the actual bug, and forgot to
# revoke the group membership. `deploy` group members can read (but not
# write) `build`'s SSH private key, which is exactly what should never be
# group-readable.
#
# Both ops_svc and build are unprivileged service accounts with no sudo
# rights — this is a lateral move to a different account at the SAME
# privilege level, not an escalation to root. (Vertical PE stays a
# separate, still-to-build path via the sysadmin SSH passphrase lead in the
# same ticket MRB-7E42D9.)
#
# ---------------------------------------------------------------------------
# SAMPLE SOLUTION (intended solve path)
# ---------------------------------------------------------------------------
# 1. SSH to Machine A as ops_svc using the IDOR-leaked creds:
#      ssh ops_svc@<machine-a-ip>        (password: N3twork_Ops_2026!)
# 2. Notice the extra group membership:
#      id ops_svc   ->   groups: ops_svc deploy
# 3. Hunt for what `deploy` actually grants access to (the ticket already
#    hinted /srv/build is where the build system lives):
#      find /srv/build -group deploy 2>/dev/null
#    -> turns up /srv/build/.ssh/id_ed25519, mode 640, owner build:deploy
# 4. Read it (group-readable, so ops_svc can cat it despite not owning it):
#      cat /srv/build/.ssh/id_ed25519 > /tmp/build_key
#      chmod 600 /tmp/build_key
# 5. Use it to log in as build directly:
#      ssh -i /tmp/build_key build@<machine-a-ip>
# 6. Read the flag:
#      cat ~/flag_horizontal.txt
#      -> FLAG{horizontal_ops_svc_group_perms_to_build}
#
# Not automatable by a generic scanner: it requires already holding
# ops_svc's creds (only obtainable via the IDOR chain), noticing an
# unexpected secondary group, and connecting that group to a specific
# path the game only hinted at via an old, easy-to-skip ticket.
#
# ---------------------------------------------------------------------------
# DECOYS / hardening notes
# ---------------------------------------------------------------------------
# - /srv/build also gets ordinary, boring Jenkins-looking files (build logs,
#   a deploy.sh) so `ls /srv/build` alone doesn't scream "look in .ssh".
# - build has NO sudo rights and is not in any privileged group — confirm
#   this stays true if you touch the box later, or you'll accidentally turn
#   this into a vertical PE path instead.
# - `build`'s account is otherwise inert (no other services run as build on
#   this box yet). If a later vertical-PE design wants a root-owned cron job
#   that executes something writable by build, that would chain nicely off
#   this foothold — flag as a "notes for report" idea, not built yet.
#
set -euo pipefail

if [[ $EUID -ne 0 ]]; then
  echo "Run this as root." >&2
  exit 1
fi

DEPLOY_GROUP="deploy"
BUILD_USER="build"
OPS_USER="ops_svc"
OPS_PASSWORD="N3twork_Ops_2026!"   # matches the OpsConsole/IDOR-leaked password (deliberate reuse)
BUILD_HOME="/home/${BUILD_USER}"
SRV_BUILD="/srv/build"

echo "[*] Creating group ${DEPLOY_GROUP} (if missing)"
getent group "${DEPLOY_GROUP}" >/dev/null || groupadd "${DEPLOY_GROUP}"

echo "[*] Creating user ${BUILD_USER}"
if ! id "${BUILD_USER}" &>/dev/null; then
  useradd -m -s /bin/bash -g "${BUILD_USER}" "${BUILD_USER}"
fi
usermod -aG "${DEPLOY_GROUP}" "${BUILD_USER}"

echo "[*] Creating user ${OPS_USER}"
if ! id "${OPS_USER}" &>/dev/null; then
  useradd -m -s /bin/bash "${OPS_USER}"
fi
echo "${OPS_USER}:${OPS_PASSWORD}" | chpasswd
# The misconfig: ops_svc should NOT be in this group. This is the leftover
# from the Jenkins-debugging story above — it's the entire vulnerability.
usermod -aG "${DEPLOY_GROUP}" "${OPS_USER}"

echo "[*] Setting up ${SRV_BUILD}"
mkdir -p "${SRV_BUILD}"
chown "${BUILD_USER}:${BUILD_USER}" "${SRV_BUILD}"
chmod 755 "${SRV_BUILD}"

# --- Decoys: boring, plausible build-system clutter ---
sudo -u "${BUILD_USER}" bash -c "cat > ${SRV_BUILD}/deploy.sh" <<'EOF'
#!/usr/bin/env bash
# Meridian Robotics — staging deploy script (Jenkins job #4471)
echo "Pulling latest staging build..."
echo "Deploying to /srv/www/staging..."
echo "Done."
EOF
chmod 755 "${SRV_BUILD}/deploy.sh"

sudo -u "${BUILD_USER}" bash -c "cat > ${SRV_BUILD}/build.log" <<'EOF'
[2026-07-02 09:10] Job #4470 SUCCESS
[2026-07-02 09:14] Job #4471 FAILED: permission denied writing /srv/build/artifacts
[2026-07-02 09:15] Retrying with sudo... escalation not permitted, ticket filed.
[2026-07-02 10:02] Job #4472 SUCCESS (workaround: ops added to deploy group temporarily)
EOF

# --- The actual secret: build's SSH key, group-readable by mistake ---
sudo -u "${BUILD_USER}" mkdir -p "${SRV_BUILD}/.ssh"
sudo -u "${BUILD_USER}" ssh-keygen -t ed25519 -N "" -C "build@meridian-robotics" \
  -f "${SRV_BUILD}/.ssh/id_ed25519" >/dev/null

mkdir -p "${BUILD_HOME}/.ssh"
cat "${SRV_BUILD}/.ssh/id_ed25519.pub" >> "${BUILD_HOME}/.ssh/authorized_keys"
chown -R "${BUILD_USER}:${BUILD_USER}" "${BUILD_HOME}/.ssh"
chmod 700 "${BUILD_HOME}/.ssh"
chmod 600 "${BUILD_HOME}/.ssh/authorized_keys"

# THE VULNERABLE PERMISSION:
chown "${BUILD_USER}:${DEPLOY_GROUP}" "${SRV_BUILD}/.ssh"
chmod 750 "${SRV_BUILD}/.ssh"                       # deploy group can traverse
chown "${BUILD_USER}:${DEPLOY_GROUP}" "${SRV_BUILD}/.ssh/id_ed25519"
chmod 640 "${SRV_BUILD}/.ssh/id_ed25519"            # deploy group can READ the private key
chown "${BUILD_USER}:${BUILD_USER}" "${SRV_BUILD}/.ssh/id_ed25519.pub"
chmod 644 "${SRV_BUILD}/.ssh/id_ed25519.pub"

echo "[*] Planting the flag"
echo "FLAG{horizontal_ops_svc_group_perms_to_build}" > "${BUILD_HOME}/flag_horizontal.txt"
chown "${BUILD_USER}:${BUILD_USER}" "${BUILD_HOME}/flag_horizontal.txt"
chmod 600 "${BUILD_HOME}/flag_horizontal.txt"

echo "[*] Confirming build has no elevated rights (should print nothing)"
groups "${BUILD_USER}" | grep -E "sudo|wheel|admin" && \
  echo "  !!! WARNING: build is in a privileged group — fix before shipping !!!" || \
  echo "  OK: build is unprivileged."

cat <<EOF

Done.

Reminder before shipping this box:
  - Confirm sshd allows password auth for ops_svc (PasswordAuthentication),
    or switch that leg to a planted key if your image disables it globally.
  - ops_svc password: ${OPS_PASSWORD}
  - Verify neither ops_svc nor build has sudo rights: 'sudo -l -U ops_svc'
    and 'sudo -l -U build' should both show "not allowed to run sudo".
EOF
