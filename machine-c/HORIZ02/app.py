from flask import Flask, request, session, redirect, url_for
import html

app = Flask(__name__)
app.secret_key = "CITS3006-HORIZ02-LAB"

USERS = {
    1: {
        "username": "analyst1",
        "password": "Analyst1_Lab_2026!",
        "role": "analyst",
        "note": "Your normal analyst1 profile."
    },
    2: {
        "username": "analyst2",
        "password": "Analyst2_Lab_2026!",
        "role": "analyst",
        "note": "CITS3006 HORIZ-02 FLAG: CITS3006{HORIZ02_IDOR_OBJECT}"
    }
}

# Halcyon Systems look & feel (distinct brand for Machine C).
SHELL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
  :root { --ink:#1b1626; --bg:#f5f4f8; --plum:#231a33; --violet:#7c5cff; --muted:#6c6580; }
  body { font-family: "Segoe UI", system-ui, -apple-system, sans-serif; background: var(--bg); margin: 0; color: var(--ink); }
  header { background: var(--plum); color: #fff; padding: 14px 28px; display: flex; justify-content: space-between; align-items: center; }
  header .brand { font-weight: 700; letter-spacing: 0.04em; display: flex; align-items: center; gap: 9px; }
  header .brand .dot { width: 12px; height: 12px; border-radius: 50%; background: var(--violet); box-shadow: 0 0 0 4px rgba(124,92,255,0.25); }
  header .brand span { color: #b9a6ff; }
  header nav a { color: #cbc3dd; text-decoration: none; margin-left: 18px; font-size: 14px; }
  header nav a:hover { color: #fff; }
  header nav span { color: #9a8fb5; font-size: 14px; margin-left: 18px; }
  main { max-width: 640px; margin: 44px auto; padding: 0 20px; }
  .card { background: #fff; border: 1px solid #e7e3ef; border-radius: 14px; padding: 26px; box-shadow: 0 6px 24px rgba(35,26,51,0.06); }
  .card + .card { margin-top: 18px; }
  h1 { font-size: 21px; margin-top: 0; }
  h2 { font-size: 16px; }
  p { line-height: 1.55; font-size: 14px; }
  a.btn, button { display: inline-block; background: var(--violet); color: #fff; border: none; padding: 10px 18px; border-radius: 8px; font-size: 14px; cursor: pointer; text-decoration: none; margin-top: 6px; font-weight: 600; }
  a.btn:hover, button:hover { background: #6a49f0; }
  a.btn.secondary { background: #efecf7; color: #4a2fd0; }
  a.btn.secondary:hover { background: #e4dff4; }
  label { display: block; font-size: 13px; color: #4b4560; margin-bottom: 4px; margin-top: 12px; }
  input[type=text], input[type=password] { width: 100%; padding: 10px 12px; border: 1px solid #d7d2e3; border-radius: 8px; font-size: 14px; box-sizing: border-box; }
  input:focus { outline: none; border-color: var(--violet); box-shadow: 0 0 0 3px rgba(124,92,255,0.15); }
  .flash { background: #fdecef; color: #a11b3b; padding: 10px 14px; border-radius: 8px; font-size: 14px; margin-bottom: 14px; }
  .meta { color: var(--muted); font-size: 12px; margin-top: 4px; }
  .field { margin-top: 14px; }
  .field .k { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.04em; }
  .field .v { font-size: 15px; margin-top: 2px; }
  .note { background: #f4f1fd; border: 1px solid #e0d8f6; border-radius: 8px; padding: 12px 14px; font-size: 14px; margin-top: 6px; white-space: pre-wrap; }
  .pill { display:inline-block; background:#efecf7; color:#4a2fd0; font-size:12px; font-weight:600; padding:3px 10px; border-radius:999px; }
</style>
</head>
<body>
<header>
  <div class="brand"><span class="dot"></span>HALCYON<span>SYSTEMS</span> &middot; Analyst Console</div>
  <nav>__NAV__</nav>
</header>
<main>__BODY__</main>
</body>
</html>"""


def page(title, body, nav=""):
    return (SHELL
            .replace("__TITLE__", title)
            .replace("__NAV__", nav)
            .replace("__BODY__", body))


@app.route("/")
def index():
    if "user_id" not in session:
        body = """
        <div class="card">
          <span class="pill">Analyst Console</span>
          <h1 style="margin-top:12px;">Halcyon Systems</h1>
          <p class="meta">Internal staging environment — Halcyon threat analysis team.</p>
          <p>Sign in to view your analyst profile and assigned case notes.</p>
          <a class="btn" href="/login">Log in</a>
        </div>
        """
        return page("Analyst Console — Halcyon Systems", body)

    uid = session["user_id"]
    uname = html.escape(USERS[uid]["username"])
    nav = f'<span>{uname}</span><a href="/logout">Log out</a>'
    body = f"""
    <div class="card">
      <span class="pill">Signed in</span>
      <h1 style="margin-top:12px;">Welcome back, {uname}</h1>
      <p class="meta">You are signed in to the Halcyon Systems Analyst Console.</p>
      <p>Review your profile record and the case note assigned to your account.</p>
      <a class="btn" href="/profile/{uid}">View my profile</a>
      <a class="btn secondary" href="/logout">Log out</a>
    </div>
    """
    return page("Analyst Console — Halcyon Systems", body, nav)


@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        for uid, user in USERS.items():
            if user["username"] == username and user["password"] == password:
                session["user_id"] = uid
                return redirect(url_for("index"))

        message = "Invalid credentials."

    flash = f'<div class="flash">{html.escape(message)}</div>' if message else ""
    body = f"""
    <div class="card">
      <h1>Sign in</h1>
      <p class="meta">Halcyon Systems — Analyst Console access.</p>
      {flash}
      <form method="POST">
        <label for="username">Username</label>
        <input type="text" id="username" name="username" autocomplete="username">
        <label for="password">Password</label>
        <input type="password" id="password" name="password" autocomplete="current-password">
        <button type="submit">Log in</button>
      </form>
    </div>
    """
    return page("Log in — Halcyon Systems", body)


@app.route("/profile/<int:user_id>")
def profile(user_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    # INTENTIONALLY VULNERABLE:
    # The application verifies that the user is logged in,
    # but does NOT verify that the requested object belongs
    # to the current user.
    user = USERS.get(user_id)

    current = html.escape(USERS[session["user_id"]]["username"])
    nav = f'<span>{current}</span><a href="/logout">Log out</a>'

    if user is None:
        body = """
        <div class="card">
          <h1>User not found</h1>
          <p>No analyst record exists for that ID.</p>
          <a class="btn secondary" href="/">Back to console</a>
        </div>
        """
        return page("Not found — Halcyon Systems", body, nav), 404

    body = f"""
    <div class="card">
      <h1>Analyst Profile</h1>
      <div class="field"><div class="k">User ID</div><div class="v">{user_id}</div></div>
      <div class="field"><div class="k">Username</div><div class="v">{html.escape(user["username"])}</div></div>
      <div class="field"><div class="k">Role</div><div class="v">{html.escape(user["role"])}</div></div>
      <div class="field"><div class="k">Case note</div><div class="note">{html.escape(user["note"])}</div></div>
      <p style="margin-top:18px;"><a class="btn secondary" href="/">Back to console</a></p>
    </div>
    """
    return page("Analyst Profile — Halcyon Systems", body, nav)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


app.run(host="0.0.0.0", port=5000)
