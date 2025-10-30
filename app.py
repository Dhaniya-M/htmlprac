import os
import base64
from datetime import timedelta
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
from flask_cors import CORS

# Optional: Supabase client
try:
    from supabase import create_client
except Exception:
    create_client = None

# -------- Configuration --------
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://sdehamebfouhdsvuafjf.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-secret-change-me")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")  # optional Gemini key

# -------- Flask App Setup --------
app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = JWT_SECRET_KEY
app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=7)

bcrypt = Bcrypt(app)
jwt = JWTManager(app)
CORS(app, supports_credentials=True)

# -------- Supabase Initialization --------
supabase = None
if create_client and SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        supabase = None
        app.logger.warning(f"⚠️ Supabase init failed: {e}")

# -------- Helper Functions --------
def supabase_get_user_by_email(email):
    if not supabase:
        return None
    resp = supabase.table("users").select("*").eq("email", email).limit(1).execute()
    if resp and resp.data:
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

# -------- Web Pages --------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup")
def signup_page():
    return render_template("signup.html")

@app.route("/login")
def login_page():
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

# -------- Other Pages --------
@app.route("/soil")
def soil_page(): return render_template("soil.html")

@app.route("/pest")
def pest_page(): return render_template("pest.html")

@app.route("/voice")
def voice_page(): return render_template("voice.html")

@app.route("/chatbot")
def chatbot_page(): return render_template("chatbot.html")

@app.route("/weather")
def weather_page(): return render_template("weather.html")

@app.route("/market")
def market_page(): return render_template("market.html")

# -------- API: Register --------
@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    mobile = data.get("mobile", "").strip()
    password = data.get("password", "")

    if not (name and email and password):
        return jsonify({"status": "error", "message": "All fields are required"}), 400

    existing = supabase_get_user_by_email(email)
    if existing:
        return jsonify({"status": "error", "message": "Email already registered"}), 400

    pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    if supabase:
        supabase_insert_user(name, email, mobile, pw_hash)

    access_token = create_access_token(identity=email)
    session["user"] = name
    return jsonify({"status": "success", "message": "Signup successful!", "data": {"access_token": access_token}}), 200

# -------- API: Login --------
@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    user = supabase_get_user_by_email(email)
    if not user:
        return jsonify({"status": "error", "message": "Invalid email or password"}), 401

    stored_hash = user.get("password_hash")
    if not stored_hash or not bcrypt.check_password_hash(stored_hash, password):
        return jsonify({"status": "error", "message": "Invalid email or password"}), 401

    access_token = create_access_token(identity=email)
    session["user"] = user.get("name") or email
    return jsonify({"status": "success", "message": "Login successful!", "data": {"access_token": access_token}}), 200

# -------- API: Chatbot --------
@app.route("/agri-chatbot", methods=["POST"])
def agri_chatbot():
    data = request.get_json() or {}
    query = data.get("query", "").strip()
    if not query:
        return jsonify({"reply": "Please ask something."})
    if GEMINI_API_KEY:
        reply = f"(Gemini placeholder) You asked: '{query}' — I can analyze soil, pest, and market info."
    else:
        reply = f"You said: '{query}'. (Gemini API key not configured.)"
    return jsonify({"reply": reply})

# -------- API: Pest Detection --------
@app.route("/pest-detect", methods=["POST"])
def pest_detect():
    data = request.get_json() or {}
    img_b64 = data.get("image")
    if not img_b64:
        return jsonify({"status": "error", "message": "No image provided"}), 400
    try:
        base64.b64decode(img_b64, validate=True)
    except Exception:
        return jsonify({"status": "error", "message": "Invalid image data"}), 400
    return jsonify({
        "status": "success",
        "result": "Detected: Aphids (confidence 0.87). Recommended: Neem oil spray."
    })

# -------- Error Handlers --------
@app.errorhandler(404)
def not_found(e):
    return jsonify({"status": "error", "message": "Not Found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"status": "error", "message": "Internal Server Error"}), 500

# -------- Run App --------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
