from flask import Flask, request, render_template,session, redirect, url_for, flash
import os
import sqlite3
import json,time,requests
from threading import Thread

app = Flask(__name__)
app.secret_key = os.urandom(24)
DB_PATH = '/app/data/database.db'
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
BOT_URL=os.environ.get("BOT_URL", "http://bot:3000/visit")
CSP_POLICY = "default-src 'self'; script-src 'self' https://cdnjs.cloudflare.com/ajax/libs/dompurify/; style-src 'self' 'unsafe-inline'; img-src 'self'; connect-src 'self'; form-action 'self'; base-uri 'self'; "
RATE_LIMIT = 20 
LAST_REPORT_TIME = {}



def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, bio TEXT DEFAULT '',admin_msg TEXT DEFAULT '', role TEXT DEFAULT 'user', note_button_color TEXT DEFAULT '#2563eb')")
    user_columns = {column[1] for column in c.execute("PRAGMA table_info(users)")}
    if 'note_button_color' not in user_columns:
        c.execute("ALTER TABLE users ADD COLUMN note_button_color TEXT DEFAULT '#2563eb'")
    c.execute("INSERT OR IGNORE INTO users (username, password,role) VALUES (?, ?, ?)", ("admin", ADMIN_PASSWORD, "admin"))
    c.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, title TEXT, content TEXT, visit_count INTEGER DEFAULT 0, FOREIGN KEY(user_id) REFERENCES users(id))")
    conn.commit()
    conn.close()

@app.after_request
def add_csp_header(response):
    response.headers['Content-Security-Policy'] = CSP_POLICY
    return response

def notify_bot(user_id):
      try:
          requests.post(BOT_URL, data={'user_id': user_id}, timeout=(3, 45))
      except requests.RequestException as error:
          app.logger.error("Bot request failed: %s", error)

init_db()

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('profile', user_id=session['user_id']))
    return redirect(url_for('login'))

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
            c.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', (username, password, 'user'))
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
        password = request.form.get('password', '')
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT id, role FROM users WHERE username=? AND password=?', (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['user_id'] = user[0]
            session['role'] = user[1]
            return redirect(url_for('profile', user_id=user[0]))
        else:
            flash("Invalid username or password", "error")
            return redirect('/login')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/user/<int:user_id>/profile', methods=['GET', 'POST'])
def profile(user_id):
    if 'user_id' not in session or 'role' not in session:
        return redirect('/login')
    if session['user_id'] != user_id and session.get('role') != 'admin':
        return "Access denied", 403
    if session.get('role') == 'admin':
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('UPDATE users SET admin_msg = ? WHERE id=?', ("Admin has visited your profile. Likely an error occurred when visiting.", user_id))
        conn.commit()
        conn.close()
    if request.method == 'POST':
        if session.get('user_id') != user_id :
            return "Access denied", 403
        bio = request.form.get('bio', '').strip()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('UPDATE users SET bio = ? WHERE id=?', (bio, user_id))
        conn.commit()
        conn.close()
        print(f"User {user_id} updated bio to: {bio}")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT username, bio, admin_msg FROM users WHERE id=?', (user_id,))
    user = c.fetchone()
    conn.close()
    if user:
        return render_template('profile.html', username=user[0], bio=user[1], admin_msg=user[2], user_id=user_id)
    else:
        return "User not found", 404

@app.route('/user/<int:user_id>/notes', methods=['GET', 'POST'])
def notes(user_id):
    if 'user_id' not in session or 'role' not in session:
        return redirect('/login')
    if session['user_id'] != user_id and session.get('role') != 'admin':
        return "Access denied", 403
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if request.method == 'POST':
        if session.get('user_id') != user_id :
            conn.close()
            return "Access denied", 403
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        if title and content:
            if len(title) > 80 or len(content) > 1000:
                conn.close()
                return "Title or content too long", 400
            c.execute('INSERT INTO notes (user_id, title, content) VALUES (?, ?, ?)', (user_id, title, content))
            conn.commit()
            conn.close()
            return redirect(url_for('notes', user_id=user_id))
    c.execute('SELECT id, title  FROM notes WHERE user_id=?', (user_id,))
    notes = c.fetchall()
    color = c.execute('SELECT note_button_color FROM users WHERE id=?', (user_id,)).fetchone()[0]
    color_input = color or '#2563eb'
    conn.commit()
    conn.close()
    note_ids = [note[0] for note in notes]
    
    return render_template(
        'notes.html',
        notes=notes,
        note_ids=note_ids,
        user_id=user_id,
        color_input=color_input
    )

@app.route('/user/<int:user_id>/preferences/button-color', methods=['POST'])
def save_button_color(user_id):
    if 'user_id' not in session or 'role' not in session:
        return "Authentication required", 401
    if session['user_id'] != user_id :
        return "Access denied", 403

    color = request.form.get('color', '').strip()
    if not color:
        return "Color is required", 400

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE users SET note_button_color = ? WHERE id=?', (color, user_id))
    conn.commit()
    conn.close()
    print(f"User {user_id} updated note button color to: {color}")
    return '', 204

@app.route('/note/<int:note_id>', methods=['GET'])
def note_detail(note_id):
    if 'user_id' not in session or 'role' not in session:
        return redirect('/login')
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if session.get('role') == 'admin':
        c.execute('SELECT id, title, content FROM notes WHERE id=?', (note_id,))
    else:
        c.execute('SELECT id, title, content FROM notes WHERE id=? AND user_id=?', (note_id, session['user_id']))
    note = c.fetchone()
    if note:
        c.execute('UPDATE notes SET visit_count = visit_count + 1 WHERE id=?', (note_id,))
        conn.commit()
        conn.close()
        return render_template('note_detail.html', note=note, user_id=session['user_id'])
    else:
        conn.close()
        return "Note not found or access denied", 404

@app.route('/note/<int:note_id>/stats', methods=['GET'])
def note_stats(note_id):
    if 'user_id' not in session or 'role' not in session:
        return redirect('/login')
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if session.get('role') == 'admin':
        c.execute('SELECT id, title, visit_count FROM notes WHERE id=?', (note_id,))
    else:
        c.execute('SELECT id, title, visit_count FROM notes WHERE id=? AND user_id=?', (note_id, session['user_id']))
    note = c.fetchone()
    conn.close()
    if note:
        return f"Note: {note[1]}, Visit Count: {note[2]}"
    else:
        return "Note not found or access denied", 404

    
@app.route('/trigger-admin', methods=['POST'])
def trigger_admin():
    if 'user_id' not in session or 'role' not in session:
        return redirect('/login')
    user_id = session['user_id']
    current_time = int(time.time())
    last_time = LAST_REPORT_TIME.get(user_id, 0)
    if current_time - last_time < RATE_LIMIT:
        return f"Rate limit exceeded. Please wait {RATE_LIMIT - (current_time - last_time)} seconds.", 429
    LAST_REPORT_TIME[user_id] = current_time
    Thread(target=notify_bot, args=(user_id,), daemon=True).start()

    return redirect(url_for('notes', user_id=user_id))
