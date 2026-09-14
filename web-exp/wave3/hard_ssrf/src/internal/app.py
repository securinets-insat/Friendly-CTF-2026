import os
from flask import Flask
PORT=int(os.environ.get("PORT", 3001))
FLAG=os.environ.get("FLAG", "Securinets{redacted}")

app = Flask(__name__)

@app.route('/internal')
def internal():
    return "ok"

@app.route('/internal/flag.txt')
def flag():
    return FLAG

if __name__ == '__main__':
    app.run('0.0.0.0', port=PORT)