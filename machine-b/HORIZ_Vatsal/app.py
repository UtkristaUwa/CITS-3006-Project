from flask import Flask, request, jsonify
import jwt

app = Flask(__name__)

# INTENTIONALLY WEAK SECRET FOR THE CTF
SECRET = "CITS3006"

USERS = {
    "analyst1": {
        "password": "Analyst1_Lab_2026!",
        "id": 1,
        "role": "analyst",
        "note": "Your analyst1 profile."
    },
    "analyst2": {
        "password": "Analyst2_Lab_2026!",
        "id": 2,
        "role": "analyst",
        "note": "CITS3006 HORIZ-03 FLAG: CITS3006{HORIZ03_JWT_FORGERY}"
    }
}

@app.route("/")
def index():
    return """
    <h1>CITS3006 Analyst API</h1>
    <p>POST /login with username and password.</p>
    <p>GET /profile with a Bearer token.</p>
    """

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    username = data.get("username", "")
    password = data.get("password", "")

    user = USERS.get(username)

    if not user or user["password"] != password:
        return jsonify({"error": "invalid credentials"}), 401

    token = jwt.encode(
        {
            "sub": username,
            "role": user["role"]
        },
        SECRET,
        algorithm="HS256"
    )

    return jsonify({"token": token})

@app.route("/profile")
def profile():
    auth = request.headers.get("Authorization", "")

    if not auth.startswith("Bearer "):
        return jsonify({"error": "missing bearer token"}), 401

    token = auth.split(" ", 1)[1]

    try:
        # INTENTIONALLY VULNERABLE:
        # The signing secret is weak and can be discovered/guessed.
        decoded = jwt.decode(token, SECRET, algorithms=["HS256"])
    except Exception:
        return jsonify({"error": "invalid token"}), 401

    username = decoded.get("sub")
    user = USERS.get(username)

    if not user:
        return jsonify({"error": "unknown user"}), 403

    return jsonify({
        "user_id": user["id"],
        "username": username,
        "role": user["role"],
        "note": user["note"]
    })

app.run(host="0.0.0.0", port=5000)
