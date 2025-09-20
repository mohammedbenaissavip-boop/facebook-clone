import sqlite3

DB_NAME = "users.db"

def view_users():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    print("\n=== Registered Users ===")
    try:
        c.execute("SELECT id, email, password FROM users")
        rows = c.fetchall()
        if rows:
            for row in rows:
                print(row)
        else:
            print("No users found.")
    except Exception as e:
        print("Error:", e)
    conn.close()

def view_attempts():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    print("\n=== Login Attempts ===")
    try:
        c.execute("SELECT id, email, password, success, timestamp FROM login_attempts ORDER BY timestamp DESC")
        rows = c.fetchall()
        if rows:
            for row in rows:
                print(row)
        else:
            print("No login attempts found.")
    except Exception as e:
        print("Error:", e)
    conn.close()

if __name__ == "__main__":
    view_users()
    view_attempts()
