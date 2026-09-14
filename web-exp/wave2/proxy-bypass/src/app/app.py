from flask import Flask, request, jsonify , render_template, redirect, url_for
import os

FLAG=os.environ.get('FLAG', 'Securinets{redacted}')

app=Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.get('/admin')
def admin():
    return jsonify({"flag": FLAG})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)