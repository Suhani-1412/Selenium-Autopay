
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
import stripe
import os
from dotenv import load_dotenv
load_dotenv()
SECRETKEY=os.getenv("APP_SECRET_KEY")
KEY=os.getenv("STRIPE_API_KEY")

app = Flask(__name__)
app.secret_key = SECRETKEY

# Stripe Test Key
stripe.api_key = KEY
YOUR_DOMAIN = "http://127.0.0.1:5000"

# ---------- DATABASE ----------
DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, password TEXT, email TEXT UNIQUE)''')
    conn.commit()
    conn.close()

def add_user(username, password, email):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                  (username, password, email))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    result = c.fetchone()
    conn.close()
    return result

def check_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    result = c.fetchone()
    conn.close()
    return result is not None

# ---------- ROUTES ----------

@app.route("/")
def home():
    session.pop("user", None)
    return render_template("index.html", user=None, error=None, success=None)

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    # ✅ check if username exists first
    if not get_user(username):
        return render_template("index.html", error="User does not exist. Please register.", user=None, success=None)

    if check_user(username, password):
        session["user"] = username
        return redirect(url_for("dashboard"))
    else:
        return render_template("index.html", error="Incorrect password", user=None, success=None)

@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username").strip()
    password = request.form.get("password")
    email = request.form.get("email").strip().lower()

    if get_user(username):
        return render_template("index.html", error="Username already taken!", user=None, success=None)

    if add_user(username, password, email):
        return render_template("index.html", success="Registration successful! Please log in.", user=None, error=None)
    else:
        return render_template("index.html", error="Email already exists!", user=None, success=None)

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("home"))
    return render_template("index.html", user=session["user"], error=None, success=None)

@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    if "user" not in session:
        return redirect(url_for("home"))

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {"name": "Test Product"},
                "unit_amount": 5000,
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url=YOUR_DOMAIN + "/success",
        cancel_url=YOUR_DOMAIN + "/cancel",
    )
    return redirect(checkout_session.url, code=303)

@app.route("/success")
def success():
    return "<h1>✅ Payment Successful</h1>"

@app.route("/cancel")
def cancel():
    return "<h1>❌ Payment Canceled</h1>"

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# ---------- RUN ----------
if __name__ == "__main__":
    init_db()
    app.run(port=5000, debug=True)
