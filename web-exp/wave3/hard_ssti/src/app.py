import sqlite3
import os
import uuid
import threading
import time
from pathlib import Path
from flask import Flask, request, jsonify, render_template,render_template_string, redirect, session, url_for

app=Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "supersecretkey")
UPLOAD_FOLDER = Path(os.environ.get("UPLOAD_FOLDER", "/app/data/uploads"))
ALLOWED_EXTENSIONS = {'txt'}
MAX_SIZE= 2*1024
app.config["MAX_CONTENT_LENGTH"] = MAX_SIZE
DB_PATH = os.environ.get("DB_PATH", "/app/data/database.db")
FLAG= os.environ.get("FLAG", "Securinets{redacted}")

def schedule_deletion(file_id: int, owner_id: int, stored_name: str, delay_seconds: float = 60):
    def _delete():
        path = UPLOAD_FOLDER / str(owner_id) / stored_name
        path.unlink(missing_ok=True)
        conn = sqlite3.connect(DB_PATH)
        conn.execute("DELETE FROM files WHERE id = ?", (file_id,))
        conn.commit()
        conn.close()

    timer = threading.Timer(delay_seconds, _delete)
    timer.daemon = True  
    timer.start()

def user_upload_dir(user_id: int) -> Path:
    d = UPLOAD_FOLDER / str(user_id)
    d.mkdir(parents=True, exist_ok=True)
    return d
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def is_safe_filename(filename: str, base_dir: Path) -> bool:
    if not filename or len(filename) > 255:
        return False

    if "\x00" in filename:
        return False

    if "/" in filename or "\\" in filename:
        return False

    if filename in (".", ".."):
        return False

    target = os.path.abspath(os.path.join(base_dir, filename))
    base = os.path.abspath(base_dir)
    if not target.startswith(base + os.sep):
        return False

    return True

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
        CREATE TABLE files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id INTEGER NOT NULL,
            stored_name TEXT NOT NULL,      
            original_name TEXT NOT NULL,
            mime_type TEXT,
            size INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def logged_in():
    return "id" in session


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
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, role FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        if user:
            session["id"] = user[0]
            session["role"] = user[1]
            conn.close()
            return redirect('/profile')
        conn.close()
        return jsonify({"error": "Invalid credentials"}), 401
    return render_template('login.html')    
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            return jsonify({"error": "Username and password required"}), 400
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, "user"))
            conn.commit()
        except sqlite3.IntegrityError:
            return jsonify({"error": "Username already exists"}), 400
        finally:
            conn.close()
        return redirect('/login')
    return render_template('register.html')

@app.route('/profile', methods=['GET','POST'])
def profile():
    if not logged_in():
        return redirect('/login')
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE id=?", (session["id"],))
    user = cursor.fetchone()
    if request.method == 'POST':
        f=request.files.get('file')
        if not f or f.filename == '':
            conn.close()
            return jsonify({"error": "No file provided"}), 400
        original_name= f.filename
        stored_name = str(uuid.uuid4()) + ".txt"
        if not allowed_file(original_name):
            conn.close()
            return jsonify({"error": "File type not allowed"}), 400
        if not is_safe_filename(original_name, user_upload_dir(session["id"])):
            conn.close()
            return jsonify({"error": "Unsafe filename"}), 400
        file_path = user_upload_dir(session["id"]) / stored_name
        f.save(file_path)
        size= os.path.getsize(file_path)
        cursor.execute(
        "INSERT INTO files (owner_id, stored_name, original_name, mime_type, size) "
        "VALUES (?, ?, ?, ?, ?)",
        (session["id"], stored_name, original_name, f.mimetype, size)
        ).lastrowid
        conn.commit()
        file_id = cursor.lastrowid
        conn.close()
        schedule_deletion(file_id, session["id"], stored_name, delay_seconds=60)
        return redirect(url_for('profile')), 302
    files= cursor.execute("SELECT id, original_name, created_at FROM files WHERE owner_id=?", (session["id"],)).fetchall()
    conn.close()
    return render_template('profile.html', user=user, files=files)

@app.route('/files/<int:file_id>', methods=['GET','POST'])
def get_file(file_id):
    if not logged_in():
        return redirect('/login')
    try:
        file_id = int(file_id)
    except ValueError:
        return jsonify({"error": "Invalid file ID"}), 400
    if not (0 < file_id < 2**63):  # SQLite INTEGER range
        return jsonify({"error": "File ID out of range"}), 400
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT stored_name, original_name FROM files WHERE id=? AND owner_id=?", (file_id, session["id"]))
    file = cursor.fetchone()
    conn.close()
    if not file:
        return jsonify({"error": "File not found"}), 404
    stored_name, original_name = file
    file_path = user_upload_dir(session["id"]) / stored_name
    if not file_path.exists():
        return jsonify({"error": "File not found on server"}), 404
    if request.method == 'GET':
        time.sleep(0.5)
        try:
            with open(file_path, 'rb') as f:
                data= f.read().decode('utf-8',errors='replace')
        except FileNotFoundError as e:
            e.filename = original_name
            template="<h1>error has been caught: {}</h1>".format(str(e))
            return render_template_string(template), 500
        return render_template('file.html', file_content=data, original_name=original_name)
        
    if request.method == 'POST':
        new_content = request.form.get('content')
        if new_content is None:
            return render_template_string("No content provided"), 400
        current_size = os.path.getsize(file_path)
        new_size = len(new_content.encode('utf-8'))+ current_size
        if new_size > MAX_SIZE:
            return render_template_string("File size exceeds the maximum limit of 2KB"), 400
        with open(file_path, 'ab') as f:
            f.write(new_content.encode('utf-8'))
    
        return redirect(url_for('get_file', file_id=file_id)), 302


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.get('/healthz')
def healthz():
    return jsonify({"status": "healthy"})


init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=False)
