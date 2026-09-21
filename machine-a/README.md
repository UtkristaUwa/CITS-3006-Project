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

## Still to do

- General hardening pass before shipping (confirm `FLASK_DEBUG` unset,
  `ops_svc`/`build` still have no sudo rights).
- Run `provision_re.sh` on the VM and verify the RE sample solve end to end.
