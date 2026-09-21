"""
Seeds portal.db for the Meridian Robotics Dev Portal (Machine A).

Run this once before starting app.py:
    python3 init_db.py
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "portal.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'developer'
);

CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ref TEXT UNIQUE NOT NULL,
    user_id INTEGER NOT NULL,
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
"""


def seed():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)

    # jchen/mfoster: developer. sysadmin: admin, the IDOR target.
    conn.execute(
        "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
        ("jchen", "Summer2024!", "developer"),
    )
    conn.execute(
        "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
        ("mfoster", "P@ssword2024", "developer"),
    )
    conn.execute(
        "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
        ("sysadmin", "R00tR0b0tics#99", "admin"),
    )

    conn.execute(
        "INSERT INTO tickets (ref, user_id, subject, body, created_at) VALUES (?, ?, ?, ?, ?)",
        (
            "MRB-1A2B3C",
            1,
            "Staging build pipeline failing",
            "Jenkins job #4471 fails on the deploy step, seeing a permissions "
            "error writing to /srv/build. Can someone take a look?",
            "2026-07-02 09:14",
        ),
    )
    conn.execute(
        "INSERT INTO tickets (ref, user_id, subject, body, created_at) VALUES (?, ?, ?, ?, ?)",
        (
            "MRB-9F0E7D",
            1,
            "VPN access request",
            "Requesting VPN access for the new intern starting Monday.",
            "2026-07-05 11:02",
        ),
    )
    conn.execute(
        "INSERT INTO tickets (ref, user_id, subject, body, created_at) VALUES (?, ?, ?, ?, ?)",
        (
            "MRB-55C81A",
            2,
            "Laptop replacement",
            "My laptop battery died completely, need a loaner while IT orders "
            "a replacement.",
            "2026-07-08 15:40",
        ),
    )
    conn.execute(
        "INSERT INTO tickets (ref, user_id, subject, body, created_at) VALUES (?, ?, ?, ?, ?)",
        (
            "MRB-B10C44",
            2,
            "Printer offline on 3rd floor",
            "The 3rd floor printer near the kitchen is showing an offline "
            "error. Can IT take a look when free?",
            "2026-07-09 10:05",
        ),
    )
    conn.execute(
        "INSERT INTO tickets (ref, user_id, subject, body, created_at) VALUES (?, ?, ?, ?, ?)",
        (
            "MRB-C7741F",
            1,
            "Wiki access request",
            "Requesting edit access to the engineering wiki space.",
            "2026-07-09 14:22",
        ),
    )
    conn.execute(
        "INSERT INTO tickets (ref, user_id, subject, body, created_at) VALUES (?, ?, ?, ?, ?)",
        (
            "MRB-E4471B",
            2,
            "Slack channel request",
            "Could someone add me to the #ops-build channel?",
            "2026-07-09 16:47",
        ),
    )
    # Decoy admin ticket -- boring, meant to be tried and rejected.
    conn.execute(
        "INSERT INTO tickets (ref, user_id, subject, body, created_at) VALUES (?, ?, ?, ?, ?)",
        (
            "MRB-2D9A88",
            3,
            "Firewall rule cleanup - low priority",
            "A few stale firewall rules from the old staging environment "
            "should be cleaned up whenever someone has spare time. Not urgent.",
            "2026-07-10 08:10",
        ),
    )
    # Real target: sysadmin's ticket, only reachable via /activity (the IDOR).
    conn.execute(
        "INSERT INTO tickets (ref, user_id, subject, body, created_at) VALUES (?, ?, ?, ?, ?)",
        (
            "MRB-7E42D9",
            3,
            "Rotate ops_svc credentials before audit",
            "Reminder to rotate the ops_svc service account before the Q3 "
            "audit. Current creds for reference: ops_svc / N3twork_Ops_2026! "
            "(used on the build/ops host, port 2222).\n\n"
            "FLAG{idor_tickets_leak_ops_creds}",
            "2026-07-10 08:21",
        ),
    )

    conn.commit()
    conn.close()
    print(f"Seeded {DB_PATH}")


if __name__ == "__main__":
    seed()
