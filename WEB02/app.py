from flask import Flask, request, make_response, render_template_string

app = Flask(__name__)

FLAG = "CITS3006{WEB02_REFLECTED_XSS}"

@app.route("/")
def index():
    return """
    <h1>CITS3006 Support Portal</h1>
    <p>Submit a message to the support search service.</p>
    <form action="/search" method="GET">
        <input name="q" placeholder="Search messages">
        <button type="submit">Search</button>
    </form>
    """

@app.route("/search")
def search():
    q = request.args.get("q", "")

    # INTENTIONALLY VULNERABLE:
    # q is inserted directly into the HTML response without escaping.
    page = """
    <h1>Support Search</h1>
    <p>Search results for: %s</p>

    <div id="results">
        <p>No matching public messages were found.</p>
    </div>

    <p><a href="/">Home</a></p>
    """ % q

    return make_response(page)

@app.route("/review")
def review():
    # Internal reviewer page intentionally contains a secret
    # in the DOM. The reflected XSS on /search executes in the
    # same origin and can read this page after navigation.
    return """
    <h1>Internal Review Console</h1>
    <div id="review-status">Reviewer access granted.</div>
    <div id="review-secret" style="display:none;">
        CITS3006{WEB02_REFLECTED_XSS}
    </div>
    <p>This page is used by the training reviewer.</p>
    """

@app.route("/help")
def help_page():
    return """
    <h1>Support Portal Help</h1>
    <p>Use the search function to locate support messages.</p>
    """

app.run(host="0.0.0.0", port=5000)
