from flask import Flask, render_template
import threading
import sys
from pynput import keyboard
import time

from app.browser_manager import BrowserManager
from app.voice_recognition import VoiceRecognition
from app.youtube_controller import YouTubeController
from app.command_processor import CommandProcessor

# Инициализация Flask
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    return 'Данные отправлены!'

def start_flask():
    app.run(debug=False)

def on_key_press(key, voice_recognition):
    try:
        if key == keyboard.Key.f2:
            is_active = voice_recognition.toggle_voice()
            if is_active:
                print("Голосовое управление ВКЛЮЧЕНО")
                voice_recognition.play_notification()
            else:
                print("Голосовое управление ВЫКЛЮЧЕНО")
    except AttributeError:
        pass

def main():
    print("Запуск голосового помощника...")
    
    try:
        # Инициализация компонентов
        browser_manager = BrowserManager()
        voice_recognition = VoiceRecognition()
        youtube_controller = YouTubeController(browser_manager)
        command_processor = CommandProcessor(browser_manager, voice_recognition, youtube_controller)
        
        # Настройка обработчика команд
        voice_recognition.set_command_processor(command_processor)
        
        # Запуск голосового помощника
        voice_recognition.start()
        
    except Exception as e:
        print(f"Ошибка при запуске: {e}")
        if 'voice_recognition' in locals():
            voice_recognition.cleanup()
        if 'browser_manager' in locals():
            browser_manager.close_browser()
        sys.exit(1)

if __name__ == "__main__":
    main() 