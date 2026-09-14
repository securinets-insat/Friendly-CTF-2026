from flask import Flask, request, jsonify , render_template, redirect, url_for
import os

app = Flask(__name__)


@app.route('/')
def index():
    return redirect(url_for('dig'))

@app.route('/dig', methods=['GET', 'POST'])
def dig():
    if request.method == 'POST':
        domain = request.form.get('domain')
        if domain:
            cmd = f"dig {domain}"
            try:
                output = os.popen(cmd).read()
                return jsonify({"domain": domain, "output": output})
            except Exception as e:
                return jsonify({"domain": domain, "error": str(e)}), 500
        else:
            return jsonify({"error": "No domain provided"}), 400
    return render_template('dig.html')