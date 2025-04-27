from flask import render_template, send_from_directory
from app import app, socketio

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/status')
def status():
    return {'status': 'active'}