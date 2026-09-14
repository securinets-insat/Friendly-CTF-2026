import sqlite3
import os
import hashlib
from flask import Flask, request, jsonify, render_template, redirect, session
app=Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "supersecretkey")
DB_PATH = "database.db"
FLAG= os.environ.get("FLAG", "Securinets{redacted}")
ADMIN_PASSWD= os.environ.get("ADMIN_PASSWD", "admin123")
md5_hash = hashlib.md5(ADMIN_PASSWD.encode('utf-8')).hexdigest()
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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL
        )
    ''')
    cursor.execute('''
    INSERT OR IGNORE INTO products (name, description, price) VALUES
    ('Mechanical Gaming Keyboard', 'RGB backlit keyboard with tactile mechanical switches', 89.99),
    ('Ergonomic Wireless Mouse', '2.4GHz wireless mouse with adjustable DPI and thumb rest', 45.50),
    ('27-Inch 4K UHD Monitor', 'IPS display panel with 144Hz refresh rate and HDR support', 329.99),
    ('Noise-Canceling Headphones', 'Over-ear wireless headphones with 30-hour battery life', 199.99),
    ('Portable 1TB NVMe SSD', 'Compact USB 3.2 solid-state drive with 1050MB/s speeds', 119.99)
    ''')
    cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)", ("admin", md5_hash, "admin"))
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
    return redirect('/products')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            return jsonify({"error": "Username and password required"}), 400
        hashed=hashlib.md5(password.encode('utf-8')).hexdigest()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, role FROM users WHERE username = ? AND password = ?", (username, hashed))
        user = cursor.fetchone()
        if user :
            session["id"] = user[0]
            session["role"] = user[1]
            return redirect('/profile')
        else:
            return jsonify({"error": "Invalid credentials"}), 401
    return render_template('login.html')    

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            return jsonify({"error": "Username and password required"}), 400
        hashed=hashlib.md5(password.encode('utf-8')).hexdigest()
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, hashed, "user"))
            conn.commit()
        except sqlite3.IntegrityError:
            return jsonify({"error": "Username already exists"}), 400
        finally:
            conn.close()
        return redirect('/login')
    return render_template('register.html')

@app.get('/products')
def products():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()
    return render_template('products.html', products=products)

@app.get('/search')
def search():
    q = request.args.get('q')
    query = f"SELECT * FROM products WHERE name LIKE '%{q}%'"
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query)
    products = cursor.fetchall()
    conn.close()
    return render_template('products.html', products=products)

@app.get('/profile')
def profile():
    if not logged_in():
        return redirect('/login')
    user_id = session.get("id")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return render_template('profile.html', user=user)

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
    app.run(host='0.0.0.0', port=5001, debug=False)