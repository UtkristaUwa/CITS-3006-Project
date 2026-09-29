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

@app.route("/")
def index():
    return """
    <h1>CITS3006 Support Portal</h1>
    <p>Search the public support messages, or report a message to a reviewer.</p>
    <form action="/search" method="GET">
        <input name="q" placeholder="Search messages">
        <button type="submit">Search</button>
    </form>
    <form action="/report" method="GET">
        <input name="q" placeholder="Text to send to a reviewer">
        <button type="submit">Report to reviewer</button>
    </form>
    """

@app.route("/search")
def search():
    q = request.args.get("q", "")
    # INTENTIONALLY VULNERABLE: q is reflected into HTML without escaping.
    page = """
    <h1>Support Search</h1>
    <p>Search results for: %s</p>
    <div id="results"><p>No matching public messages were found.</p></div>
    <p><a href="/">Home</a></p>
    """ % q
    return make_response(page)

@app.route("/report")
def report():
    # A solver submits a payload here; the reviewer bot will visit
    # /search?q=<payload> with its privileged cookie.
    q = request.args.get("q", "")
    if q:
        with _lock:
            _queue.append(q)
    return "<p>Thanks — a reviewer will look at this shortly.</p><p><a href='/'>Home</a></p>"

@app.route("/review")
def review():
    # Only the reviewer (who holds REVIEWER_COOKIE) may see the secret.
    if request.cookies.get("reviewer") != REVIEWER_COOKIE:
        return "<h1>Internal Review Console</h1><p>Access denied.</p>", 403
    return """
    <h1>Internal Review Console</h1>
    <div id="review-status">Reviewer access granted.</div>
    <div id="review-secret">%s</div>
    """ % FLAG

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
    return "<h1>Exfiltrated</h1><pre>" + "\n".join(items) + "</pre>"

@app.route("/queue")
def queue():
    # Bot-only: hand out and clear pending payloads.
    if request.args.get("token") != BOT_TOKEN:
        return jsonify([]), 403
    with _lock:
        items = list(_queue); _queue.clear()
    return jsonify(items)

app.run(host="0.0.0.0", port=5000)
