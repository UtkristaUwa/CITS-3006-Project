# Machine A — ADV: AES-CTR Nonce Reuse (chain link to root)

**Category:** Advanced — cryptographic vulnerability
**Originally built by:** Vraj (was standalone `advanced/adv-01-aes-ctr`; now embedded in Machine A's root path)

## Role in Machine A's chain
This is **not a side-quest** — it is the link between horizontal PE and vertical PE.
The sysadmin SSH key passphrase is no longer written in the clear. `provision_vertical_pe.sh`
places two files inside the `sysadmin_home.tar.gz` pre-audit backup (which `build` can read):

- `audit_record_sample.txt` — the **known plaintext** (a routine audit-log record)
- `audit_capture.txt` — the **nonce** + the audit-log ciphertext + the protected-secret ciphertext

The backup tool reused the same AES-CTR key **and** nonce for both records, so the keystream
recovered from the known audit log decrypts the protected secret — which contains the
**sysadmin key passphrase** and the ADV flag. Without solving this, the encrypted key from
the backup is useless and there is no path to root.

```
build  ──reads backup──▶  audit_capture.txt (AES-CTR, reused nonce)
                                │  break nonce reuse with audit_record_sample.txt
                                ▼
                passphrase M3ridian_D3v!  +  CITS3006{ADV01_AES_CTR_NONCE_REUSE}
                                │  unlock sysadmin's encrypted SSH key
                                ▼
                    ssh sysadmin@A ──▶ NOPASSWD sudo ──▶ root
```

## Vulnerability
Same AES-CTR (key, nonce) reused for two messages ⇒ identical keystream.
`keystream = known_pt ⊕ known_ct`; `secret = secret_ct ⊕ keystream`.

## Sample solve
```python
kp = open("audit_record_sample.txt","rb").read().rstrip(b"\n")
# from audit_capture.txt:
kc = bytes.fromhex("<audit-log ciphertext>")
sc = bytes.fromhex("<protected-secret ciphertext>")
ks = bytes(a ^ b for a, b in zip(kp, kc))
print(bytes(a ^ b for a, b in zip(sc, ks)).decode())
# -> sysadmin ssh key passphrase: M3ridian_D3v!
#    CITS3006{ADV01_AES_CTR_NONCE_REUSE}
```

## Flag
`CITS3006{ADV01_AES_CTR_NONCE_REUSE}`

## Setup
Handled by `provision_vertical_pe.sh` (it copies these files into the backup).
To regenerate the ciphertexts offline: `pip install -r requirements.txt && python3 generate.py`.
The AES key is never placed on the VM.

## Fix
Never reuse a (key, nonce) pair in CTR/GCM; random 96-bit nonce per message, or a
nonce-misuse-resistant AEAD (AES-GCM-SIV). And never protect a live passphrase with a training key.
