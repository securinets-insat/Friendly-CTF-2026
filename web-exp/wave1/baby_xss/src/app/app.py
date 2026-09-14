import sqlite3
import os
from flask import Flask, request, jsonify, render_template, redirect, session, flash
import requests

app=Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", os.urandom(32))
DB_PATH = os.environ.get("DB_PATH", "/app/data/database.db")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")
BOT_URL=os.environ.get("BOT_URL", "http://bot:3000/visit")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, role TEXT DEFAULT 'user')''')
    c.execute('''CREATE TABLE IF NOT EXISTS reports (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,title TEXT, content TEXT, FOREIGN KEY(user_id) REFERENCES users(id))''')
    c.execute('''INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)''', ("admin", ADMIN_PASSWORD, "admin"))
    conn.commit()
    conn.close()


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect('/reports')
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if not username or not password:
            flash("Username and password cannot be empty", "error")
            return redirect('/register')
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            conn.close()
            return redirect('/login')
        except sqlite3.IntegrityError:
            conn.close()
            return "Username already exists", 400
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT id, role FROM users WHERE username=? AND password=?', (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['user_id'] = user[0]
            session['role'] = user[1]
            return redirect('/reports')
        else:
            flash("Invalid username or password", "error")
            return redirect('/login')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/reports', methods=['GET', 'POST'])
def reports():
    if 'user_id' not in session:
        return redirect('/login')
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        if not title or not content:
            flash("Title and content cannot be empty", "error")
            return redirect('/reports')
        c.execute('INSERT INTO reports (user_id, title, content) VALUES (?, ?, ?)', (session['user_id'], title, content))
        conn.commit()
        flash("Report submitted successfully", "success")
    if session.get('role') == 'admin':
        c.execute('SELECT id, title FROM reports')
    else:
        c.execute('SELECT id, title FROM reports WHERE user_id=?', (session['user_id'],))
    reports = c.fetchall()
    conn.close()
    return render_template('reports.html', reports=reports)

@app.route('/report/<int:report_id>', methods=['GET'])
def report_detail(report_id):
    if 'user_id' not in session:
        return redirect('/login')
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if session.get('role') == 'admin':
        c.execute('SELECT id, title, content FROM reports WHERE id=?', (report_id,))
    else:
        c.execute('SELECT id, title, content FROM reports WHERE id=? AND user_id=?', (report_id, session['user_id']))
    report = c.fetchone()
    conn.close()
    if report:
        return render_template('report_detail.html', report=report)
    else:
        return "Report not found or access denied", 404

@app.route('/report-to-admin', methods=['POST'])
def report_to_admin():
    if 'user_id' not in session:
        return redirect('/login')
    report_id = request.form.get('report_id')
    report_id=int(report_id) if report_id and report_id.isdigit() else None
    if not report_id :
        flash("Report ID is required", "error")
        return redirect('/reports')
    conn= sqlite3.connect(DB_PATH)
    c=conn.cursor()
    c.execute('SELECT id FROM reports WHERE id=? AND user_id=?', (report_id, session['user_id']))
    report=c.fetchone()
    conn.close()
    if not report:
        flash("Report not found ", "error")
        return redirect('/reports')
    try:
        requests.post(BOT_URL, data={'report_id': report_id}, timeout=19)
        flash("Report sent to admin for review", "success")
    except requests.exceptions.RequestException as e:
        flash("Failed to send report to admin", "error")
        print(f"Error sending report to admin: {e}")
    return redirect('/reports')

init_db()

