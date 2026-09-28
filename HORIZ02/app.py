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

@app.route("/")
def index():
    if "user_id" not in session:
        return """
        <h1>Analyst Portal</h1>
        <p><a href="/login">Login</a></p>
        """

    uid = session["user_id"]

    return f"""
    <h1>Analyst Portal</h1>
    <p>Logged in as: <b>{html.escape(USERS[uid]["username"])}</b></p>
    <p><a href="/profile/{uid}">View my profile</a></p>
    <p><a href="/logout">Logout</a></p>
    """

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

    return f"""
    <h1>Analyst Portal Login</h1>
    <p>{html.escape(message)}</p>
    <form method="POST">
        <label>Username:</label><br>
        <input name="username"><br><br>
        <label>Password:</label><br>
        <input type="password" name="password"><br><br>
        <button type="submit">Login</button>
    </form>
    """

@app.route("/profile/<int:user_id>")
def profile(user_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    # INTENTIONALLY VULNERABLE:
    # The application verifies that the user is logged in,
    # but does NOT verify that the requested object belongs
    # to the current user.
    user = USERS.get(user_id)

    if user is None:
        return "<h2>User not found</h2>", 404

    return f"""
    <h1>User Profile</h1>
    <p><b>User ID:</b> {user_id}</p>
    <p><b>Username:</b> {html.escape(user["username"])}</p>
    <p><b>Role:</b> {html.escape(user["role"])}</p>
    <p><b>Note:</b> {html.escape(user["note"])}</p>
    <p><a href="/">Home</a></p>
    """

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

app.run(host="0.0.0.0", port=5000)
