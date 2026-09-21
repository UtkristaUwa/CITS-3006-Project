#!/usr/bin/env bash
#
# provision_horizontal_pe.sh — Machine A (horizontal privilege escalation)
# CITS3006 CTF project — Meridian Robotics Dev Portal
#
# Run ONCE, as root, directly on the real Machine A VM after the base OS is
# installed and before the box ships. Deliberately OS-level (real users,
# groups, permissions) rather than another Flask service.
#
# Vuln: ops_svc (creds leaked via the web IDOR) is a leftover member of the
# `deploy` group, which can read (not write) build's SSH private key.
# Lateral move to a same-privilege account, not an escalation to root.
# Full write-up: see the Exploit Report doc.
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
  # No -g: Ubuntu's useradd auto-creates a private group named after the
  # user; "-g build" would instead require a group "build" to pre-exist.
  useradd -m -s /bin/bash "${BUILD_USER}"
fi
usermod -aG "${DEPLOY_GROUP}" "${BUILD_USER}"

echo "[*] Creating user ${OPS_USER}"
if ! id "${OPS_USER}" &>/dev/null; then
  useradd -m -s /bin/bash "${OPS_USER}"
fi
echo "${OPS_USER}:${OPS_PASSWORD}" | chpasswd
# The misconfig, and the entire vulnerability: ops_svc should not be here.
usermod -aG "${DEPLOY_GROUP}" "${OPS_USER}"

echo "[*] Setting up ${SRV_BUILD}"
mkdir -p "${SRV_BUILD}"
chown "${BUILD_USER}:${BUILD_USER}" "${SRV_BUILD}"
chmod 755 "${SRV_BUILD}"

# Decoys: boring, plausible build-system clutter.
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

# The actual secret: build's SSH key, group-readable by mistake.
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
echo "FLAG{H0RiZ0n7aL_is_D0N3_nd_dUS73d}" > "${BUILD_HOME}/flag_horizontal.txt"
chown "${BUILD_USER}:${BUILD_USER}" "${BUILD_HOME}/flag_horizontal.txt"
chmod 600 "${BUILD_HOME}/flag_horizontal.txt"

echo "[*] Confirming build has no elevated rights (should print nothing)"
groups "${BUILD_USER}" | grep -E "sudo|wheel|admin" && \
  echo "  !!! WARNING: build is in a privileged group — fix before shipping !!!" || \
  echo "  OK: build is unprivileged."

cat <<EOF

Done.

  - ops_svc password: ${OPS_PASSWORD} (confirm sshd allows password auth
    for ops_svc, or plant a key instead if your image disables it globally)
  - Verify neither ops_svc nor build has sudo: 'sudo -l -U ops_svc' /
    'sudo -l -U build' should both show "not allowed to run sudo"
  - Next: run provision_vertical_pe.sh
EOF
