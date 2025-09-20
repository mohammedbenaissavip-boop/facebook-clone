from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

DB_NAME = "users.db"

# --- Database Setup ---
def init_db():
    new_db = not os.path.exists(DB_NAME)
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    if new_db:
        c.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        c.execute("""
            CREATE TABLE login_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT,
                password TEXT,
                success INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Insert a test user
        c.execute("INSERT INTO users (email, password) VALUES (?, ?)", 
                  ("test@example.com", "password123"))
        conn.commit()
    conn.close()

# --- Routes ---
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    user = c.fetchone()

    # enregistrer la tentative
    if user:
        c.execute("INSERT INTO login_attempts (email, password, success) VALUES (?, ?, ?)", 
                  (email, password, 1))
        conn.commit()
        conn.close()
        session["user"] = email
        return redirect(url_for("dashboard"))
    else:
        c.execute("INSERT INTO login_attempts (email, password, success) VALUES (?, ?, ?)", 
                  (email, password, 0))
        conn.commit()
        conn.close()
        return render_template("index.html", error="❌ Identifiants invalides.")

@app.route("/dashboard")
def dashboard():
    if "user" in session:
        return render_template("dashboard.html", user=session["user"])
    return redirect(url_for("home"))

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
