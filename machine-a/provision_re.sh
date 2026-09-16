#!/usr/bin/env bash
#
# provision_re.sh — Machine A (reverse-engineering vulnerability)
# CITS3006 CTF project — Meridian Robotics Dev Portal
#
# Run this as root. Independent of the other three provisioning scripts —
# doesn't need ops_svc/build/sysadmin to exist first, and doesn't feed or
# depend on the PE chain. This is deliberately a separate skill test, not
# another link in the same escalation ladder.
#
# ---------------------------------------------------------------------------
# THE VULNERABILITY (for the report / exploit map)
# ---------------------------------------------------------------------------
# /opt/meridian-tools/meridian-diag is a small compiled C "firmware
# diagnostic utility" — the kind of internal tool an ops/build team would
# actually have lying around. It's world-readable and executable (any
# authenticated user on the box can run it — no special privilege
# required), but running it just prompts for an "engineer unlock code."
#
# The code and the flag are both stored XOR-encoded against a hardcoded
# key inside the binary, not in plaintext — so `strings meridian-diag`
# reveals nothing useful. Solving it requires actually disassembling the
# binary (Ghidra, objdump -d, or single-stepping in gdb) to recover the
# XOR key and the comparison logic, then either deriving the correct
# unlock code or patching the conditional jump so any input succeeds.
#
# This is intentionally NOT gated behind horizontal or vertical PE —
# anyone who's reached the box at all (e.g. via the ops_svc foothold from
# the network vuln / IDOR chain) can find and copy off this binary and
# reverse it entirely on their own machine, offline. It's meant to test a
# distinct skill (static/dynamic binary analysis), not be another rung on
# the same privilege ladder.
#
# Source lives in this repo at machine-a/re-challenge/meridian_diag.c for
# the report — it is NEVER copied onto the VM itself, only the compiled,
# stripped binary. Compiling on the box (rather than shipping a
# pre-built binary) keeps it correctly linked for whatever base image the
# VM actually uses.
#
# ---------------------------------------------------------------------------
# SAMPLE SOLUTION (intended solve path)
# ---------------------------------------------------------------------------
# 1. From any OS foothold on the box (e.g. ops_svc), notice the tool:
#      ls -la /opt/meridian-tools/
# 2. Copy it off (scp, or cat | base64 over the same SSH session) to your
#    own machine so you can throw real tooling at it.
# 3. `strings meridian-diag` shows nothing useful — the code/flag are
#    XOR-encoded, not plaintext. `file meridian-diag` shows it's a
#    stripped, dynamically linked ELF binary.
# 4. Disassemble (Ghidra/objdump -d/gdb) the comparison loop in `main` —
#    it XORs each input byte against a repeating 8-byte key ("Meridian",
#    visible once you spot the key array's bytes: 4d 65 72 69 64 69 61 6e)
#    and compares against a second hardcoded byte array.
# 5. XOR-decode that second array against the same key to recover the
#    real unlock code, OR just patch the `jne`/conditional jump after the
#    comparison so any input is accepted.
# 6. Run it and enter the recovered code (or the patched binary with
#    anything): `./meridian-diag` -> `FLAG{re_xor_unlock_meridian_diag}`
#
# Not solvable by `strings`, brute force (17-character keyspace), or any
# automated web/network scanner — genuinely requires binary analysis.
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

echo "[*] Fetching source into a private build directory (never left on disk after)"
# This script expects meridian_diag.c to sit alongside it (i.e. in
# machine-a/re-challenge/ in the repo, same relative layout used here).
SRC="$(dirname "$0")/re-challenge/meridian_diag.c"
if [[ ! -f "${SRC}" ]]; then
  echo "Can't find meridian_diag.c — expected it at ${SRC}" >&2
  exit 1
fi
cp "${SRC}" "${BUILD_DIR}/meridian_diag.c"

echo "[*] Compiling (optimized, stripped -- no debug symbols)"
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

Done.

${TOOLS_DIR}/meridian-diag is installed, world-executable, source is not
on the VM. Any authenticated user on the box (ops_svc, build, sysadmin)
can find and copy it off to reverse locally.
EOF
