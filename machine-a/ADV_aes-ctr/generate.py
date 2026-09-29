from Crypto.Cipher import AES
from pathlib import Path

# Machine A ADV — AES-CTR nonce reuse. This regenerates the two on-box files
# (known_plaintext.txt + challenge.txt). The KEY is NEVER shipped to the VM.
# provision_vertical_pe.sh copies these into the sysadmin backup archive so the
# passphrase is only recoverable by breaking the reused key/nonce.

KEY   = b"CITS3006_ADV1KEY"     # 16-byte training key (stays off-box)
NONCE = b"CITS3006NONCE12"      # 15 bytes; reused for both records == same keystream

known_pt = (b"MERIDIAN OPS AUDIT LOG 2026-07-09: routine pre-audit sweep completed; "
            b"no customer data touched; verification step passed nominally; entry closes here.")

# The protected secret: the sysadmin key passphrase used by provision_vertical_pe.sh,
# plus the ADV-01 flag. Must fit within the known-plaintext keystream length.
secret_pt = (b"sysadmin ssh key passphrase: M3ridian_D3v!\n"
             b"CITS3006{ADV01_AES_CTR_NONCE_REUSE}\n")
assert len(secret_pt) <= len(known_pt)

known_ct  = AES.new(KEY, AES.MODE_CTR, nonce=NONCE).encrypt(known_pt)
secret_ct = AES.new(KEY, AES.MODE_CTR, nonce=NONCE).encrypt(secret_pt)

Path("known_plaintext.txt").write_bytes(known_pt + b"\n")
Path("challenge.txt").write_text(
    "ADV (Machine A) - AES-CTR Nonce Reuse\n\n"
    "The pre-audit backup tool encrypted two records with AES-CTR and reused the\n"
    "same key+nonce. One record (the audit log) is recoverable in the clear from\n"
    "audit_record_sample.txt; the other holds the sysadmin key passphrase.\n\n"
    f"Nonce (hex): {NONCE.hex()}\n"
    f"Audit-log ciphertext (hex): {known_ct.hex()}\n"
    f"Protected-secret ciphertext (hex): {secret_ct.hex()}\n")
print("ADV (Machine A) challenge regenerated.")
