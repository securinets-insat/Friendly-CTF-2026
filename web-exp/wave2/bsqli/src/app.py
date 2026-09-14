import sqlite3
import os
from flask import Flask, request, jsonify, render_template, redirect, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
app=Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "supersecretkey")
FLAG= os.environ.get("FLAG", "Securinets{redacted}")
ADMIN_PASSWD= os.environ.get("ADMIN_PASSWD", "admin123")
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_HOST = os.environ['DB_HOST']
DB_PORT = os.environ['DB_PORT']
DB_NAME = os.environ['DB_NAME']
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='user')

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)

class SearchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ts = db.Column(db.DateTime, default=db.func.current_timestamp())
    ip = db.Column(db.String(45), nullable=False)
    term = db.Column(db.String(255), nullable=False)


def init_db():
    with app.app_context(): 
        db.create_all()
        if not Product.query.first():
            products = [
                Product(name='Mechanical Gaming Keyboard', description='RGB backlit keyboard with tactile mechanical switches', price=89.99),
                Product(name='Ergonomic Wireless Mouse', description='2.4GHz wireless mouse with adjustable DPI and thumb rest', price=45.50),
                Product(name='27-Inch 4K UHD Monitor', description='IPS display panel with 144Hz refresh rate and HDR support', price=329.99),
                Product(name='Noise-Canceling Headphones', description='Over-ear wireless headphones with 30-hour battery life', price=199.99),
                Product(name='Portable 1TB NVMe SSD', description='Compact USB 3.2 solid-state drive with 1050MB/s speeds', price=119.99),
            ]
            db.session.add_all(products)

        if not User.query.filter_by(username='admin').first():
            db.session.add(User(username='admin', password=ADMIN_PASSWD, role='admin'))

        db.session.commit()

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
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session["id"] = user.id
            session["role"] = user.role
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
        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username already exists"}), 400
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')

@app.get('/products')
def products():
    products = Product.query.all()
    return render_template('products.html', products=products)

@app.get('/search')
def search():
    q = request.args.get('q')
    products = Product.query.filter(Product.name.like(f'%{q}%')).all()
    return render_template('products.html', products=products)

@app.route('/search_log', methods=['POST'])
def search_log():
    data = request.get_json(silent=True) or {}
    term = data.get('term', '')
    ip= request.remote_addr
    
    query = f"INSERT INTO search_history (ts,ip,term) VALUES (NOW(),'{ip}','{term}')"
    db.session.execute(text(query))
    db.session.commit()

    return jsonify({"status": "logged"})


@app.get('/profile')
def profile():
    if not logged_in():
        return redirect('/login')
    user_id = session.get("id")
    user = User.query.get(user_id)
    return render_template('profile.html', user=user)

@app.get('/admin')
@admin_required
def admin():
    search_history = []
    search_history = SearchHistory.query.order_by(SearchHistory.ts.desc()).all()
    return render_template('admin.html', flag=FLAG, search_history=search_history)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.get('/healthz')
def healthz():
    return jsonify({"status": "healthy"})


init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=False)