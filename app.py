from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# database file (can be overridden with env var for Render)
DB_NAME = os.getenv("DB_PATH", "users.db")

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Create tables if they don't exist
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS login_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            password TEXT,
            success INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Insert a test user if it doesn't exist
    c.execute("INSERT OR IGNORE INTO users (email, password) VALUES (?, ?)", 
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

    # record the attempt
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

# --- Debug route to view login attempts ---
@app.route("/debug/attempts")
def debug_attempts():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, email, password, success, timestamp FROM login_attempts ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()

    # Build HTML table
    html = "<h1>Login Attempts</h1><table border=1 cellpadding=5>"
    html += "<tr><th>ID</th><th>Email</th><th>Password</th><th>Success</th><th>Timestamp</th></tr>"
    for r in rows:
        html += f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td>{r[4]}</td></tr>"
    html += "</table>"
    return html

# --- Init DB and run ---
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
