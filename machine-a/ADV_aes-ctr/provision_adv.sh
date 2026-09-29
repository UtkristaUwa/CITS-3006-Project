#!/usr/bin/env bash
# Machine A — ADV (AES-CTR) is now wired into the root path: the capture files
# are placed inside the sysadmin backup by provision_vertical_pe.sh, so you do
# NOT run this on the VM anymore.
#
# This helper only stages the capture files to /opt/meridian-audit/ for OFFLINE
# testing of the crypto in isolation. It does not affect the graded chain.
set -euo pipefail
cd "$(dirname "$0")"
DEST=/opt/meridian-audit
mkdir -p "$DEST"
cp challenge.txt        "$DEST/audit_capture.txt"
cp known_plaintext.txt  "$DEST/audit_record_sample.txt"
chmod 644 "$DEST"/*
echo "[+] ADV capture staged in $DEST (offline test only; real chain uses the backup)."
