#!/usr/bin/env bash
#
# provision_re.sh — Machine A (reverse-engineering vulnerability)
# CITS3006 CTF project — Meridian Robotics Dev Portal
#
# Run as root. Independent of the other provisioning scripts and the PE
# chain — reachable from any foothold, deliberately a separate skill test.
#
# Vuln: /opt/meridian-tools/meridian-diag is a small compiled C tool whose
# unlock code and flag are XOR-encoded against a hardcoded key, so `strings`
# reveals nothing and solving it requires actual disassembly. Source lives
# at re-challenge/meridian_diag.c, never shipped on the VM, only compiled
# here fresh each time. Full write-up: see the Exploit Report doc.
#
set -euo pipefail

if [[ $EUID -ne 0 ]]; then
  echo "Run this as root." >&2
  exit 1
fi

if ! command -v gcc &>/dev/null; then
  echo "[*] Installing build-essential (gcc not found)"
  apt-get update -qq
  apt-get install -y -qq build-essential
fi

TOOLS_DIR="/opt/meridian-tools"
BUILD_DIR=$(mktemp -d)

echo "[*] Compiling source into a private build dir"
SRC="$(dirname "$0")/re-challenge/meridian_diag.c"
if [[ ! -f "${SRC}" ]]; then
  echo "Can't find meridian_diag.c — expected it at ${SRC}" >&2
  exit 1
fi
cp "${SRC}" "${BUILD_DIR}/meridian_diag.c"
gcc -O2 -s -o "${BUILD_DIR}/meridian-diag" "${BUILD_DIR}/meridian_diag.c"

echo "[*] Installing to ${TOOLS_DIR}"
mkdir -p "${TOOLS_DIR}"
cp "${BUILD_DIR}/meridian-diag" "${TOOLS_DIR}/meridian-diag"
chown root:root "${TOOLS_DIR}/meridian-diag"
chmod 755 "${TOOLS_DIR}/meridian-diag"   # world-readable + executable, not writable

rm -rf "${BUILD_DIR}"

echo "[*] Sanity check (should print the flag)"
echo "R0b0t1cs-Eng-7734" | "${TOOLS_DIR}/meridian-diag"

echo "[*] Confirming the secret doesn't leak via strings (should print nothing)"
strings "${TOOLS_DIR}/meridian-diag" | grep -iE "flag\{|R0b0t1cs|7734" && \
  echo "  !!! WARNING: secret is leaking via strings — investigate the build !!!" || \
  echo "  OK: nothing leaked via strings."

cat <<EOF

Done. ${TOOLS_DIR}/meridian-diag installed, world-executable, source not on
the VM. Any authenticated user on the box can find and copy it off.
EOF
