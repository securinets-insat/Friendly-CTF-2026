import sqlite3
import os
from flask import Flask, request, jsonify, render_template,render_template_string, redirect, session
app=Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "supersecretkey")
DB_PATH = os.environ.get("DB_PATH", "/app/data/database.db")
FLAG= os.environ.get("FLAG", "Securinets{redacted}")

PROFILE_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>profile — friendly-sqli</title>
<style>
:root {{
--bg: #ffffff;
--fg: #111111;
--muted: #666666;
--line: #cccccc;
}}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; height: 100%; }}
body {{
background: var(--bg);
color: var(--fg);
font-family: ui-monospace, "SF Mono", "Cascadia Code", Consolas, monospace;
font-size: 15px;
line-height: 1.6;
display: flex;
align-items: center;
justify-content: center;
}}
main {{ width: 100%; max-width: 480px; padding: 48px 24px; }}
.tag {{
font-size: 12px;
letter-spacing: 0.08em;
text-transform: uppercase;
color: var(--muted);
margin: 0 0 8px;
}}
h1 {{ font-size: 22px; font-weight: 600; margin: 0 0 28px; }}
label {{ display: block; font-size: 12px; color: var(--muted); margin: 0 0 6px; }}
.field {{ padding: 14px 16px; border: 1px solid var(--line); margin: 0 0 16px; }}
textarea.field {{
width: 100%;
font-family: inherit;
font-size: inherit;
color: inherit;
border-color: var(--line);
resize: vertical;
min-height: 80px;
}}
button {{
display: inline-block;
padding: 10px 18px;
border: 1px solid var(--fg);
background: var(--bg);
color: var(--fg);
font-family: inherit;
font-size: 13px;
cursor: pointer;
margin: 0 0 28px;
}}
button:hover {{ background: var(--fg); color: var(--bg); }}
footer {{ margin-top: 32px; font-size: 12px; }}
footer a {{ color: var(--muted); }}
</style>
</head>
<body>
<main>
<p class="tag">Securinets · web</p>
<h1>Profile</h1>
<label for="username">username</label>
<div class="field" id="username">{{{{ user[0] }}}}</div>
<label for="bio">bio</label>
<div class="field" id="bio">{bio}</div>
<form method="POST" action="/profile">
<label for="bio_input">update bio</label>
<textarea class="field" id="bio_input" name="bio"></textarea>
<button type="submit">Save</button>
</form>
<footer><a href="/logout">log out</a></footer>
</main>
</body>
</html>"""
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            bio TEXT DEFAULT 'This is my bio.'
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

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if not logged_in():
        return redirect('/login')
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT username, bio FROM users WHERE id=?", (session["id"],))
    user = cursor.fetchone()
    if request.method == 'POST':
        new_bio = request.form.get('bio')
        cursor.execute("UPDATE users SET bio=? WHERE id=?", (new_bio, session["id"]))
        conn.commit()
        return redirect('/profile')
    conn.close()
    bio=user[1] 
    template=PROFILE_TEMPLATE.format(bio=bio)
    return render_template_string(template, user=user)
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.get('/healthz')
def healthz():
    return jsonify({"status": "healthy"})


init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=False)