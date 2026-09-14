"""
Meridian Robotics Dev Portal — Machine A (web vulnerability: IDOR)

Intentionally vulnerable Flask app for the CITS3006 CTF project.
DO NOT deploy this anywhere internet-facing outside the controlled CTF
network -- it is deliberately insecure.
"""

import os
import sqlite3
from functools import wraps

from flask import Flask, abort, flash, redirect, render_template, request, session, url_for

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "templates"),
    static_folder=os.path.join(os.path.dirname(__file__), "machine-a", "static"),
)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-not-for-prod-CHANGE-ME")

DB_PATH = os.path.join(os.path.dirname(__file__), "machine-a", "portal.db")

# Static flavor data for /activity -- not a DB table. Leaks which ticket refs
# exist and who touched them without leaking ticket content, so recon
# (finding a ref) and exploitation (viewing that ref) happen on separate
# pages. Sorted newest-first by ts.
ACTIVITY_LOG = [
    {"ts": "2026-07-10 08:21", "actor": "sysadmin", "action": "opened ticket", "ref": "MRB-7E42D9"},
    {"ts": "2026-07-10 08:10", "actor": "sysadmin", "action": "opened ticket", "ref": "MRB-2D9A88"},
    {"ts": "2026-07-09 16:47", "actor": "mfoster", "action": "opened ticket", "ref": "MRB-E4471B"},
    {"ts": "2026-07-09 14:22", "actor": "jchen", "action": "opened ticket", "ref": "MRB-C7741F"},
    {"ts": "2026-07-09 10:05", "actor": "mfoster", "action": "opened ticket", "ref": "MRB-B10C44"},
    {"ts": "2026-07-08 15:40", "actor": "mfoster", "action": "opened ticket", "ref": "MRB-55C81A"},
    {"ts": "2026-07-05 11:02", "actor": "jchen", "action": "opened ticket", "ref": "MRB-9F0E7D"},
    {"ts": "2026-07-02 09:14", "actor": "jchen", "action": "opened ticket", "ref": "MRB-1A2B3C"},
]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return wrapper


@app.route("/")
def index():
    return redirect(url_for("dashboard") if "user_id" in session else url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        db.close()

        if user and user["password"] == password:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("dashboard"))

        flash("Invalid username or password.")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    tickets = db.execute(
        "SELECT id, ref, subject, created_at FROM tickets WHERE user_id = ?",
        (session["user_id"],),
    ).fetchall()
    db.close()
    return render_template("dashboard.html", tickets=tickets, username=session["username"])


# --------------------------------------------------------------------------
# Team activity feed -- a legitimate "team visibility" feature that leaks
# cross-user data because nobody scoped it: every authenticated user sees
# the exact same full list of all ticket refs, regardless of who they are.
# This is where recon happens (which refs exist); exploitation happens on
# the /ticket/<ref> page below.
# --------------------------------------------------------------------------
@app.route("/activity")
@login_required
def activity():
    return render_template("activity.html", entries=ACTIVITY_LOG)


# --------------------------------------------------------------------------
# VULNERABLE ENDPOINT — Insecure Direct Object Reference (IDOR)
#
# The ticket is looked up purely by the `ref` supplied in the URL. There is
# no check that `tickets.user_id == session['user_id']`, so any
# authenticated user can read any other user's ticket simply by knowing its
# ref -- including tickets never linked from their own dashboard.
# --------------------------------------------------------------------------
@app.route("/ticket/<ref>")
@login_required
def view_ticket(ref):
    db = get_db()
    ticket = db.execute(
        "SELECT tickets.*, users.username, users.role FROM tickets "
        "JOIN users ON tickets.user_id = users.id "
        "WHERE tickets.ref = ?",
        (ref,),
    ).fetchone()
    db.close()

    if ticket is None:
        abort(404)

    is_own_ticket = ticket["user_id"] == session["user_id"]

    return render_template("ticket.html", ticket=ticket, is_own_ticket=is_own_ticket)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
