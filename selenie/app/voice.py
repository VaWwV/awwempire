import speech_recognition as sr
import threading
import time
from queue import Queue, Empty
import pygame
from flask import Flask, render_template
from pynput import keyboard
import sys
from browser_manager import BrowserManager

# Инициализация Flask
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    return 'Данные отправлены!'

class VoiceAssistant:
    def __init__(self):
        # Инициализация компонентов
        self.browser = BrowserManager()
        self.recognizer = sr.Recognizer()
        self.command_queue = Queue()
        
        # Состояния
        self.is_running = True
        self.is_input_mode = False
        self.is_voice_active = True
        
        # Звуковые эффекты
        pygame.mixer.init()
        self.notification_sound = pygame.mixer.Sound("icq.mp3")

    def play_notification(self):
        self.notification_sound.play()

    def on_key_press(self, key):
        if key == keyboard.Key.f2:
            self.is_voice_active = not self.is_voice_active
            self.is_input_mode = False
            if self.is_voice_active:
                print("Голосовое управление ВКЛЮЧЕНО")
                self.play_notification()
            else:
                print("Голосовое управление ВЫКЛЮЧЕНО")

    def listen_voice(self):
        print("Инициализация микрофона...")
        try:
            with sr.Microphone() as source:
                print("Настройка уровня шума...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print("Слушаю...")
                
                while self.is_running:
                    if not self.is_voice_active:
                        time.sleep(0.1)
                        continue
                        
                    try:
                        audio = self.recognizer.listen(source, timeout=0.5, phrase_time_limit=3)
                        self.process_audio(audio)
                    except sr.WaitTimeoutError:
                        continue
                    except Exception as e:
                        print(f"Ошибка при прослушивании: {e}")
                        time.sleep(1)
        except Exception as e:
            print(f"Критическая ошибка микрофона: {e}")
            self.is_running = False

    def process_audio(self, audio):
        try:
            command = self.recognizer.recognize_google(audio, language='ru-RU')
            if command:
                self.play_notification()
                self.command_queue.put(command.lower())
                print(f"Распознано: {command}")
        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            print(f"Ошибка сервиса распознавания: {e}")

    def process_commands(self):
        while self.is_running:
            try:
                command = self.command_queue.get(timeout=0.1)
                self.execute_command(command)
            except Empty:
                continue

    def execute_command(self, command):
        print(f"Выполняю команду: {command}")
        
        if "стоп" in command:
            self.stop()
        elif "открой youtube" in command:
            self.browser.open_url("https://www.youtube.com")
        elif "обнови страницу" in command:
            self.browser.refresh_page()
        elif command.startswith("листай"):
            direction = "up" if "вверх" in command else "down"
            self.browser.scroll_page(direction)
        # Добавьте другие команды по необходимости

    def start(self):
        print("Голосовой помощник запущен")
        print("Голосовое управление ВКЛЮЧЕНО")
        
        try:
            # Запуск Flask
            flask_thread = threading.Thread(target=lambda: app.run(debug=False))
            flask_thread.daemon = True
            flask_thread.start()
            
            # Запуск слушателя клавиатуры
            keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
            keyboard_listener.daemon = True
            keyboard_listener.start()
            
            # Запуск распознавания голоса
            voice_thread = threading.Thread(target=self.listen_voice)
            voice_thread.daemon = True
            voice_thread.start()
            
            # Обработка команд в основном потоке
            self.process_commands()
            
        except KeyboardInterrupt:
            print("\nПрограмма остановлена пользователем")
        except Exception as e:
            print(f"Критическая ошибка: {e}")
        finally:
            self.stop()

    def stop(self):
        self.is_running = False
        self.browser.close_browser()
        sys.exit(0)

if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.start() 