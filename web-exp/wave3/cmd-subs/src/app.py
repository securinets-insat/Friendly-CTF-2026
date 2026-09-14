from flask import Flask, request,  redirect, url_for, render_template
import os

app = Flask(__name__)
ALLOWED_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.{}$`^")

@app.route('/')
def index():
    return redirect(url_for('vault'))

@app.route('/vault', methods=['GET', 'POST'])
def vault():
    if request.method == 'POST':
        input = request.form.get('input')
        if input:
            if not all(c in ALLOWED_CHARS for c in input):
                return render_template('vault.html', output="Invalid input.")
            try:
                cmd="ping -c 2 "+ input
                status = os.system(cmd)
                if status == 0:
                    output = "Exit code: 0"
                else:
                    output = "Failure"
                return render_template('vault.html', output=output)
            except Exception :
                return render_template('vault.html', output="Something went wrong.")
    return render_template('vault.html', output=None)