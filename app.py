import os
import base64
from datetime import timedelta

from flask import (
    Flask, render_template, request, jsonify, session, redirect, url_for
)
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
from flask_cors import CORS

# Supabase client
try:
    from supabase import create_client
except Exception:
    create_client = None

# --------- Configuration ---------
SUPABASE_URL = "https://sdehamebfouhdsvuafjf.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNkZWhhbWViZm91aGRzdnVhZmpmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE3Mjk0MzksImV4cCI6MjA3NzMwNTQzOX0.xKde6gz7YuuKwyz-mG94ajIG9n_Ibz7RasgTLoxRaRI"

JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-secret-change-me")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")  # optional

# --------- App & Extensions ---------
app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = JWT_SECRET_KEY
app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=7)

bcrypt = Bcrypt(app)
jwt = JWTManager(app)
CORS(app, supports_credentials=True)

# Initialize Supabase client
supabase = None
if create_client and SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        supabase = None
        app.logger.warning("Failed to initialize Supabase client: %s", e)
else:
    app.logger.warning("Supabase not configured: set SUPABASE_URL and SUPABASE_KEY")

# --------- Helper functions ---------
def supabase_get_user_by_email(email):
    if not supabase:
        return None
    resp = supabase.table("users").select("*").eq("email", email).limit(1).execute()
    if resp and resp.data and len(resp.data) > 0:
        return resp.data[0]
    return None

def supabase_insert_user(name, email, mobile, password_hash):
    if not supabase:
        return None
    resp = supabase.table("users").insert({
        "name": name,
        "email": email,
        "mobile": mobile,
        "password_hash": password_hash
    }).execute()
    return resp

# --------- Routes: Render templates ---------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup_page():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        mobile = request.form.get("mobile", "").strip()
        password = request.form.get("password", "")

        if not (name and email and password):
            return render_template("signup.html", error="All fields are required")

        existing = supabase_get_user_by_email(email) if supabase else None
        if existing:
            return render_template("signup.html", error="Email already registered")

        pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        if supabase:
            resp = supabase_insert_user(name, email, mobile, pw_hash)
            if getattr(resp, "status_code", None) and resp.status_code >= 400:
                return render_template("signup.html", error="Registration failed")
        else:
            session["dev_user"] = {"name": name, "email": email, "mobile": mobile, "password_hash": pw_hash}

        session["user"] = name
        return redirect(url_for("home"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not (email and password):
            return render_template("login.html", error="Email and password required")

        user = supabase_get_user_by_email(email) if supabase else session.get("dev_user")
        if not user:
            return render_template("login.html", error="Invalid email or password")

        stored_hash = user.get("password_hash")
        if not stored_hash or not bcrypt.check_password_hash(stored_hash, password):
            return render_template("login.html", error="Invalid email or password")

        session["user"] = user.get("name") or email
        return redirect(url_for("home"))

    return render_template("login.html")


@app.route("/home")
def home():
    user = session.get("user")
    if not user:
        return redirect(url_for("login_page"))
    return render_template("home.html", user=user)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/soil")
def soil_page():
    return render_template("soil.html")

@app.route("/pest")
def pest_page():
    return render_template("pest.html")

@app.route("/voice")
def voice_page():
    return render_template("voice.html")

@app.route("/chatbot")
def chatbot_page():
    return render_template("chatbot.html")

@app.route("/weather")
def weather_page():
    return render_template("weather.html")

@app.route("/market")
def market_page():
    return render_template("market.html")


# --------- API: Optional JSON endpoints (Supabase-backed) ---------
auth_prefix = "/api"

@app.route(f"{auth_prefix}/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify({"status":"success","message":"Hello, you accessed a protected route","user": current_user})


# --------- API: Chatbot ---------
@app.route("/agri-chatbot", methods=["POST"])
def agri_chatbot():
    payload = request.get_json() or {}
    query = payload.get("query", "").strip()
    if not query:
        return jsonify({"reply": "Please ask something."})

    if GEMINI_API_KEY:
        reply = f"(Gemini placeholder) I understood: {query}. I can give soil, pest and market tips."
    else:
        reply = f"I heard: {query}. (No model key set — set GEMINI_API_KEY to get smarter responses.)"

    return jsonify({"reply": reply})


# --------- API: Pest detection ---------
@app.route("/pest-detect", methods=["POST"])
def pest_detect():
    payload = request.get_json() or {}
    img_b64 = payload.get("image")
    if not img_b64:
        return jsonify({"status":"error","message":"No image provided"}), 400

    try:
        _ = base64.b64decode(img_b64, validate=True)
    except Exception as e:
        return jsonify({"status":"error","message":"Invalid image data", "error": str(e)}), 400

    mock_result = "Detected: Aphids (confidence 0.87). Recommended: Neem oil spray or introduce ladybugs."
    return jsonify({"status":"success", "result": mock_result})


# --------- Error handlers ---------
@app.errorhandler(400)
def bad_request(e):
    return jsonify({"status":"error","message":"Bad Request","data":{}}), 400

@app.errorhandler(401)
def unauthorized(e):
    return jsonify({"status":"error","message":"Unauthorized","data":{}}), 401

@app.errorhandler(404)
def not_found(e):
    return jsonify({"status":"error","message":"Not Found","data":{}}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"status":"error","message":"Internal Server Error","data":{}}), 500


# --------- Run ---------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
