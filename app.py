from flask import Flask, render_template, request
import datetime
import main

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', year=datetime.datetime.now().year)

@app.route('/run', methods=['POST'])
def run_agent():
    # Call the logic in main.py
    logs = main.run_agent()
    return render_template('index.html', logs=logs, year=datetime.datetime.now().year)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
