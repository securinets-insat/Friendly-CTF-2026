from flask import Flask, request, make_response, redirect, url_for, render_template
import jwt
import os
import sqlite3  
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key')
FLAG= os.environ.get('FLAG', 'Securinets{redacted}')
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

init_db()
@app.route('/')
def index():
    return redirect(url_for('game'))

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
            token = jwt.encode({'user_id': user[0], 'username': user[1],'game-status': 'playing', 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1), 'iat': datetime.datetime.utcnow()}, app.config['SECRET_KEY'], algorithm='HS256')
            resp = make_response(redirect(url_for('game')))
            resp.set_cookie('token', token)
            return resp
        else:
            return "Invalid credentials", 401
    return render_template('login.html')

@app.route('/logout')
def logout():
    resp = make_response(redirect(url_for('login')))
    resp.set_cookie('token', '', expires=0)
    return resp

@app.route('/game', methods=['GET', 'POST'])
def game():
    token = request.cookies.get('token')
    if not token:
        return redirect(url_for('login'))
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = data['user_id']
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT username FROM users WHERE id=?", (user_id,))
        user = c.fetchone()
        conn.close()
        if user:
            if request.method == 'POST':
                if not request.form.get('guess', ''):
                    return "Guess is required", 400
                try:
                    user_guess = float(request.form.get('guess', ''))
                except ValueError:
                    return "Invalid guess", 400
                computer_guess = user_guess + 1
                game_status = 'victory' if user_guess > computer_guess else 'defeat'
                new_token = jwt.encode({'user_id': user_id, 'username': user[0], 'game-status': game_status, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1), 'iat': datetime.datetime.utcnow()}, app.config['SECRET_KEY'], algorithm='HS256')
                resp = make_response(render_template('game.html', username=user[0], computer_guess=computer_guess, user_guess=user_guess))
                resp.set_cookie('token', new_token)
                return resp
            
            game_status = data.get('game-status')
            if game_status == 'victory':
                return render_template('game.html', username=user[0],  message=f"Congratulations! You won! Here is your flag: {FLAG}")
            else:
                return render_template('game.html', username=user[0],  message="You have to win to get your gift!")
        else:
            return "User not found", 404
    except jwt.ExpiredSignatureError:
        return "Token has expired", 401
    except jwt.InvalidTokenError:
        return "Invalid token", 401

    