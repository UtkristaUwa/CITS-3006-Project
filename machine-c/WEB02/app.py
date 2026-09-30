from flask import Flask, request, make_response, jsonify
import os, threading

app = Flask(__name__)

FLAG = "CITS3006{WEB02_REFLECTED_XSS}"
# Shared secret the reviewer bot presents. The flag is only served to a client
# holding this cookie — i.e. the bot — so a solver must make the BOT's browser
# read it via XSS, not just request /review themselves.
REVIEWER_COOKIE = os.environ.get("REVIEWER_COOKIE", "r3v13w-s3ss-2026")
# Token the bot uses to pull the review queue (not guessable by solvers).
BOT_TOKEN = os.environ.get("BOT_TOKEN", "bot-internal-1f4c")

_lock = threading.Lock()
_queue = []          # payloads awaiting the reviewer bot
_stolen = []         # data exfiltrated by a successful XSS

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
  main { max-width: 680px; margin: 44px auto; padding: 0 20px; }
  .card { background: #fff; border: 1px solid #e7e3ef; border-radius: 14px; padding: 26px; box-shadow: 0 6px 24px rgba(35,26,51,0.06); }
  .card + .card { margin-top: 18px; }
  h1 { font-size: 21px; margin-top: 0; }
  p { line-height: 1.55; font-size: 14px; }
  .lead { color: var(--muted); }
  form.inline { display: flex; gap: 10px; margin-top: 14px; }
  form.inline input[type=text] { flex: 1; padding: 10px 12px; border: 1px solid #d7d2e3; border-radius: 8px; font-size: 14px; box-sizing: border-box; }
  form.inline input:focus { outline: none; border-color: var(--violet); box-shadow: 0 0 0 3px rgba(124,92,255,0.15); }
  a.btn, button { display: inline-block; background: var(--violet); color: #fff; border: none; padding: 10px 18px; border-radius: 8px; font-size: 14px; cursor: pointer; text-decoration: none; font-weight: 600; white-space: nowrap; }
  a.btn:hover, button:hover { background: #6a49f0; }
  a.btn.secondary { background: #efecf7; color: #4a2fd0; }
  a.btn.secondary:hover { background: #e4dff4; }
  .results { margin-top: 16px; border-top: 1px solid #eee7f5; padding-top: 14px; }
  .empty { color: var(--muted); font-size: 14px; }
  .pill { display:inline-block; background:#efecf7; color:#4a2fd0; font-size:12px; font-weight:600; padding:3px 10px; border-radius:999px; }
  .console { background:#1c1530; color:#e7dfff; border-radius:10px; padding:16px 18px; font-family:ui-monospace,Consolas,monospace; font-size:13px; }
  .console .ok { color:#8effc4; }
  .footer-link { margin-top: 18px; }
</style>
</head>
<body>
<header>
  <div class="brand"><span class="dot"></span>HALCYON<span>SYSTEMS</span> &middot; Support Portal</div>
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
    body = """
    <div class="card">
      <span class="pill">Support Portal</span>
      <h1 style="margin-top:12px;">How can we help?</h1>
      <p class="lead">Search the public support knowledge base, or report a message to a Halcyon reviewer.</p>
      <form class="inline" action="/search" method="GET">
        <input type="text" name="q" placeholder="Search support messages…">
        <button type="submit">Search</button>
      </form>
      <form class="inline" action="/report" method="GET">
        <input type="text" name="q" placeholder="Text to send to a reviewer…">
        <button type="submit">Report to reviewer</button>
      </form>
    </div>
    """
    return page("Support Portal — Halcyon Systems", body)


@app.route("/search")
def search():
    q = request.args.get("q", "")
    # INTENTIONALLY VULNERABLE: q is reflected into HTML without escaping.
    # Built with plain concatenation so the raw payload is preserved exactly.
    body = (
        '<div class="card">'
        '<h1>Support Search</h1>'
        '<p class="lead">Search results for: ' + q + '</p>'
        '<div class="results"><p class="empty">No matching public messages were found.</p></div>'
        '<p class="footer-link"><a class="btn secondary" href="/">Back to portal</a></p>'
        '</div>'
    )
    return make_response(page("Search — Halcyon Systems", body))


@app.route("/report")
def report():
    # A solver submits a payload here; the reviewer bot will visit
    # /search?q=<payload> with its privileged cookie.
    q = request.args.get("q", "")
    if q:
        with _lock:
            _queue.append(q)
    body = """
    <div class="card">
      <h1>Thanks for the report</h1>
      <p class="lead">A Halcyon reviewer will look at this shortly.</p>
      <p class="footer-link"><a class="btn secondary" href="/">Back to portal</a></p>
    </div>
    """
    return page("Report received — Halcyon Systems", body)


@app.route("/review")
def review():
    # Only the reviewer (who holds REVIEWER_COOKIE) may see the secret.
    if request.cookies.get("reviewer") != REVIEWER_COOKIE:
        body = """
        <div class="card">
          <h1>Internal Review Console</h1>
          <div class="console">Access denied.</div>
        </div>
        """
        return page("Review Console — Halcyon Systems", body), 403
    body = (
        '<div class="card">'
        '<h1>Internal Review Console</h1>'
        '<div class="console"><div id="review-status" class="ok">Reviewer access granted.</div>'
        '<div id="review-secret">' + FLAG + '</div>'
        # Chain pivot: the reviewer-only console also carries an internal ops note.
        # Exfiltrating it points the attacker at the next stage (NET-02 rsync).
        '<div id="review-note">INTERNAL OPS: legacy file-sync is still exposed via '
        'rsync on tcp/1873 (module: legacy-sync). Pull it and rotate the analyst '
        'credentials before the audit.</div></div>'
        '</div>'
    )
    return page("Review Console — Halcyon Systems", body)


@app.route("/exfil")
def exfil():
    # Endpoint the injected script posts the stolen secret to. Self-contained:
    # the solver reads it back from /stolen (no external server needed).
    data = request.args.get("data", "")
    if data:
        with _lock:
            _stolen.append(data)
    return ("", 204)


@app.route("/stolen")
def stolen():
    with _lock:
        items = list(_stolen)
    body = (
        '<div class="card">'
        '<h1>Exfiltrated Data</h1>'
        '<div class="console">' + ("<br>".join(items) if items else "(nothing captured yet)") + '</div>'
        '</div>'
    )
    return page("Exfiltrated — Halcyon Systems", body)


@app.route("/queue")
def queue():
    # Bot-only: hand out and clear pending payloads.
    if request.args.get("token") != BOT_TOKEN:
        return jsonify([]), 403
    with _lock:
        items = list(_queue); _queue.clear()
    return jsonify(items)


app.run(host="0.0.0.0", port=5000)
