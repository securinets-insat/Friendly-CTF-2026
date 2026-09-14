import sqlite3
import os
from flask import Flask, request, jsonify, render_template, redirect, session
app=Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "supersecretkey")
DB_PATH = "database.db"
FLAG= os.environ.get("FLAG", "Securinets{redacted}")
ADMIN_PASSWD= os.environ.get("ADMIN_PASSWD", "admin123")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    ''')
    cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)", ("admin", ADMIN_PASSWD, "admin"))
    conn.commit()
    conn.close()

def logged_in():
    return "id" in session

def admin_required(f):
    def wrapper(*args, **kwargs):
        if not logged_in():
            return redirect('/login')
        if session.get("role") != "admin":
            return jsonify({"error": "Unauthorized"}), 403
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@app.get('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            return jsonify({"error": "Username and password required"}), 400
        query = f"SELECT id, role FROM users WHERE username = '{username}' AND password = '{password}'"
        conn = sqlite3.connect(DB_PATH)
        user= conn.execute(query).fetchone()
        conn.close()
        if user:
            session["id"] = user[0]
            session["role"] = user[1]           
            if user[1] == 'admin':
                return redirect('/admin')
        else:
            return jsonify({"error": "Invalid credentials"}), 401
    return render_template('login.html')    


@app.get('/admin')
@admin_required
def admin():
    return render_template('admin.html', flag=FLAG)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.get('/healthz')
def healthz():
    return jsonify({"status": "healthy"})


init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)