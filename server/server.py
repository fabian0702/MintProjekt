#!/usr/bin/python3
from flask import Flask, render_template
from api import api, filteredResults

app = Flask(__name__)

@app.get('/')
def home():
    return render_template('index.html')

if __name__ == "__main__":
    app.register_blueprint(api, url_prefix='/api')
    app.run(port=5000, host='0.0.0.0')   