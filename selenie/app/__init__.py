# Этот файл может быть пустым 
print("Инициализация пакета приложени")  # Добавили для отслеживания импорта 

from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app)

from app import routes 