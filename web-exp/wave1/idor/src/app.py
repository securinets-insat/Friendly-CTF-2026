import os
from flask import Flask, request, session, redirect, url_for, render_template
import sqlite3
import random

app = Flask(__name__)
app.secret_key = os.urandom(24)
FLAG=os.environ.get('FLAG', 'Securinets{redacted}')
ADMIN_PASSWORD=os.environ.get('ADMIN_PASSWORD', 'adminpass')
DB_PATH = os.environ.get("DB_PATH", "/app/data/database.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
    c.execute('''INSERT OR IGNORE INTO users (id, username, password) VALUES (1, 'admin', ?)''', (ADMIN_PASSWORD,))
    c.execute('''INSERT OR IGNORE INTO users (id, username, password) VALUES (2, 'user', 'userpass')''')
    c.execute('''CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, user_id INTEGER, note TEXT, FOREIGN KEY(user_id) REFERENCES users(id))''')
    conn.commit()
    conn.close()

def create_flag_list(flag):
    notes=[]
    for ch in flag:
        notes.append(ch)
        junk_len=random.randint(3,7)
        for _ in range(junk_len):
            notes.append('not here')
    return notes

def store_flag_in_db(flag):
    notes=create_flag_list(flag)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for note in notes:
        c.execute('INSERT INTO notes (user_id, note) VALUES (?, ?)', (1, note))
    conn.commit()
    conn.close()

def seed_user_notes():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for i in range(3):
        c.execute('INSERT INTO notes (user_id, note) VALUES (?, ?)', (2, 'this is a user note'))
    conn.commit()
    conn.close()

init_db()
store_flag_in_db(FLAG)
seed_user_notes()

@app.route('/')
def index():
    if 'id' in session:
        return redirect(url_for('notes'))
    return redirect(url_for('login'))


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
            session['id'] = user[0]
            session['username'] = user[1]
            return redirect(url_for('notes'))
        else:
            return "Invalid credentials", 401
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/notes')
def notes():
    if 'id' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, note FROM notes WHERE user_id=?', (session['id'],))
    notes = c.fetchall()
    conn.close()
    return render_template('notes.html', notes=notes)


@app.get('/notes/<int:note_id>')
def get_note(note_id):
    if 'id' not in session:
        return redirect(url_for('login'))
    note_id = int(note_id)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT note FROM notes WHERE id=?', (note_id,))
    note = c.fetchone()
    conn.close()
    if note:
        return render_template('note.html', note=note[0])
    else:
        return "Note not found", 404
