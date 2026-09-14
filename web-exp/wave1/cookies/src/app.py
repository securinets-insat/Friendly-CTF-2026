from flask import Flask, request, redirect, url_for, render_template,session, make_response
import os
import sqlite3
import base64
PORT=os.getenv("PORT", 5010)
FLAG=os.getenv("FLAG", "Securinets{redacted}")


app=Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "supersecretkey")
DB_PATH = os.environ.get("DB_PATH", "/app/data/database.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')    
    conn.commit()
    conn.close()    

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('profile'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if not username or not password:
            return "Username and password required", 400
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
        except sqlite3.IntegrityError:
            return "Username already exists", 400
        finally:
            conn.close()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if not username or not password:
            return "Username and password required", 400
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            is_admin = False
            encoded=base64.b64encode(str(is_admin).encode('utf-8')).decode('utf-8')
            resp = make_response(redirect(url_for('profile')))
            resp.set_cookie('is_admin', encoded)
            return resp
        else:
            return "Invalid credentials", 401
    return render_template('login.html')

@app.get('/profile')
def profile():
    is_admin_cookie = request.cookies.get('is_admin')
    if not session.get('user_id'):
        return redirect(url_for('login'))
    if not is_admin_cookie:
        return redirect(url_for('login'))
    try:
        is_admin = base64.b64decode(is_admin_cookie).decode('utf-8') == 'True'
    except Exception:
        return "Invalid cookie", 400
    if is_admin:
        msg=f'Welcome admin! Here is the flag: {FLAG}'
        return render_template('profile.html', msg=msg)
    else:
        return render_template('profile.html', msg='Welcome user! You needd more priviliges to access sensitive information.')   

@app.route('/logout')
def logout():
    session.clear()
    resp = make_response(redirect(url_for('login')))
    resp.delete_cookie('is_admin')
    return resp


init_db()
