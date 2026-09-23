from flask import Flask, request, render_template_string

app = Flask(__name__)

FLAG = "CITS3006{WEB03_SSTI_TEMPLATE_INJECTION}"

@app.route("/")
def index():
    return """
    <h1>CITS3006 Report Generator</h1>
    <p>Enter your display name to generate a report.</p>

    <form action="/report" method="GET">
        <input name="name" placeholder="Display name">
        <button type="submit">Generate Report</button>
    </form>
    """

@app.route("/report")
def report():
    name = request.args.get("name", "guest")

    # INTENTIONALLY VULNERABLE:
    # User input is incorporated into a Jinja template
    # and then rendered by the server.
    template = f"""
    <h1>Training Report</h1>
    <p>Prepared for: {name}</p>
    <p>Report generation completed.</p>
    """

    return render_template_string(template)

@app.route("/about")
def about():
    return """
    <h1>About</h1>
    <p>CITS3006 internal report-generation training application.</p>
    """

app.run(host="0.0.0.0", port=5000)
