# Machine A — Meridian Robotics Dev Portal

CITS3006 CTF project — Machine A. Public-facing dev/staging server for the
fictional company Meridian Robotics (an internal ticketing portal).

Vulns: web (IDOR), network (ARP spoofing / plaintext creds), horizontal PE
(group misconfig), vertical PE (leaked backup), RE (XOR-encoded binary).
Full write-up, sample solves, and flags: see the Exploit Report and Solve
Guide docs.

## Setup

```bash
cd machine-a
pip install -r requirements.txt --break-system-packages   # or use a venv
python3 init_db.py                                        # (re)seeds portal.db
python3 app.py                                             # runs on 0.0.0.0:5000
```

On the real VM, also run, in order:

```bash
sudo bash provision_horizontal_pe.sh
sudo bash provision_vertical_pe.sh
sudo bash provision_re.sh
```


## Full attack chain and how it is meant to be solved

        ┌──────────────── ENTRY POINT 1: WEB ────────────────┐
        │ Log in as a developer (jchen / mfoster)             │
        │   → /activity   (RECON: leaks every ticket ref,     │
        │                  including sysadmin's MRB-7E42D9)    │
        │   → /ticket/MRB-7E42D9   (IDOR: no ownership check)  │
        │      leaks: FLAG 1, ops_svc creds, passphrase lead   │
        └──────────────────────────────────────────────────────┘
                                │
        ┌──────────── ENTRY POINT 2: NETWORK ────────────────┐
        │ Get on the segment → ARP spoof / port mirror        │
        │   → Wireshark filter tcp.port == 2222               │
        │   → Follow TCP Stream → read plaintext creds        │
        │      (ops_svc AND sysadmin, in the clear)           │
        │   → connect to OpsConsole as sysadmin, run `status` │
        │      → FLAG 2                                        │
        │   password reuse: sysadmin creds ALSO log into web  │
        └──────────────────────────────────────────────────────┘
                                │  (either path yields ops_svc creds)
                                ▼
        SSH to Machine A as ops_svc
                                │
                                ▼  HORIZONTAL PE (group misconfig)
         ops_svc is in `deploy` → deploy can READ /srv/build/.ssh/id_ed25519
         → ssh -i stolen_key build@A  → FLAG 3 (/home/build/flag_horizontal.txt)
                                │
                                ▼  VERTICAL PE (leaked backup)
         as build, read /srv/build/backups/pre-audit-2026-07-09/sysadmin_home.tar.gz
          → contains sysadmin's ENCRYPTED ssh key + backup_notes.txt (passphrase M3ridian_D3v!)
         → ssh -i sysadmin_key (passphrase) sysadmin@A
          → sysadmin has NOPASSWD sudo → sudo cat /root/flag_vertical.txt → FLAG 4

         ── independent side quest, reachable from ANY shell ──
         REVERSE ENGINEERING
         copy /opt/meridian-tools/meridian-diag off-box → disassemble
          → recover XOR key "Meridian" → decode unlock code R0b0t1cs-Eng-7734
          → run tool, enter code → FLAG 5

   