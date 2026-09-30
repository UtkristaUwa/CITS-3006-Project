from flask import Flask, request, render_template_string

app = Flask(__name__)

FLAG = "CITS3006{WEB03_SSTI_TEMPLATE_INJECTION}"

# ---------------------------------------------------------------------------
# Evergreen Analytics look & feel (distinct brand for Machine B).
# A uses "Meridian Robotics" (navy/blue); C uses "Halcyon Systems"
# (plum/violet). B is a forest-green / emerald "Reporting Portal".
# ---------------------------------------------------------------------------
STYLE = """
<style>
  :root {
    --ink:#10241c; --bg:#eef4f0; --forest:#0b3d2e; --emerald:#2fbf71;
    --emerald-dk:#249a5b; --muted:#5c6f66; --line:#dbe6df;
  }
  * { box-sizing: border-box; }
  body { font-family: "Inter", "Segoe UI", system-ui, -apple-system, sans-serif;
         background: var(--bg); margin: 0; color: var(--ink); }
  header { background: var(--forest); color: #fff; padding: 15px 30px;
           display: flex; justify-content: space-between; align-items: center; }
  header .brand { font-weight: 800; letter-spacing: 0.05em; font-size: 16px;
                  display: flex; align-items: center; gap: 10px; }
  header .brand .leaf { width: 14px; height: 14px; border-radius: 50% 0 50% 50%;
                        background: var(--emerald); transform: rotate(45deg);
                        box-shadow: 0 0 0 4px rgba(47,191,113,0.22); }
  header .brand span { color: #8ee6b4; }
  header nav a { color: #bcd6c9; text-decoration: none; margin-left: 20px; font-size: 14px; }
  header nav a:hover { color: #fff; }
  main { max-width: 720px; margin: 44px auto; padding: 0 20px; }
  .card { background: #fff; border: 1px solid var(--line); border-radius: 14px;
          padding: 28px; box-shadow: 0 8px 26px rgba(11,61,46,0.07); }
  h1 { font-size: 21px; margin-top: 0; }
  .lead { color: var(--muted); font-size: 14px; line-height: 1.55; }
  .tag { display:inline-block; background:#e3f4ea; color:var(--emerald-dk);
         font-size:12px; font-weight:700; padding:4px 11px; border-radius:999px;
         letter-spacing:0.03em; margin-bottom:14px; }
  label { display:block; font-size:13px; color:var(--muted); margin:14px 0 5px; font-weight:600; }
  input[type=text] { width:100%; padding:11px 12px; border:1px solid #cdddd3;
                     border-radius:9px; font-size:14px; }
  input[type=text]:focus { outline:none; border-color:var(--emerald);
                           box-shadow:0 0 0 3px rgba(47,191,113,0.18); }
  button { margin-top:20px; background:var(--emerald); color:#063a26; font-weight:700;
           border:none; padding:11px 20px; border-radius:9px; font-size:14px; cursor:pointer; }
  button:hover { background:var(--emerald-dk); color:#fff; }
  .report { margin-top:16px; border-top:1px solid var(--line); padding-top:16px;
            line-height:1.6; font-size:14.5px; }
  .report .field { color:var(--muted); font-size:12px; text-transform:uppercase;
                   letter-spacing:0.04em; }
  footer { text-align:center; color:var(--muted); font-size:12px; margin:30px 0; }
</style>
"""

HEADER = """
<header>
  <div class="brand"><span class="leaf"></span>EVERGREEN&nbsp;<span>ANALYTICS</span> &middot; Reporting Portal</div>
  <nav>
    <a href="/">Home</a>
    <a href="/about">About</a>
  </nav>
</header>
"""

FOOTER = '<footer>Evergreen Analytics — internal reporting environment</footer>'


@app.route("/")
def index():
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Evergreen Analytics · Reporting Portal</title>{STYLE}</head><body>
{HEADER}
<main>
  <div class="card">
    <span class="tag">REPORT BUILDER</span>
    <h1>Generate a training report</h1>
    <p class="lead">Enter your display name and we'll prepare a personalised
       report summary for your Evergreen Analytics workspace.</p>
    <form action="/report" method="GET">
      <label for="name">Display name</label>
      <input type="text" id="name" name="name" placeholder="e.g. Jordan Avery">
      <button type="submit">Generate report</button>
    </form>
  </div>
</main>
{FOOTER}
</body></html>"""


@app.route("/report")
def report():
    name = request.args.get("name", "guest")

    # INTENTIONALLY VULNERABLE:
    # User input is incorporated into a Jinja template
    # and then rendered by the server. (Unchanged challenge logic.)
    template = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Report · Evergreen Analytics</title>{STYLE}</head><body>
{HEADER}
<main>
  <div class="card">
    <span class="tag">TRAINING REPORT</span>
    <h1>Report ready</h1>
    <div class="report">
      <div class="field">Prepared for</div>
      <p>{name}</p>
      <div class="field">Status</div>
      <p>Report generation completed.</p>
    </div>
  </div>
</main>
{FOOTER}
</body></html>"""

    return render_template_string(template)


@app.route("/about")
def about():
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>About · Evergreen Analytics</title>{STYLE}</head><body>
{HEADER}
<main>
  <div class="card">
    <span class="tag">ABOUT</span>
    <h1>About this portal</h1>
    <p class="lead">The Evergreen Analytics Reporting Portal is an internal
       report-generation training application used by the data operations team.</p>
  </div>
</main>
{FOOTER}
</body></html>"""


app.run(host="0.0.0.0", port=5000)
