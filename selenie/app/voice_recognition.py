print("Загрузка voice_recognition.py...")

import logging
import os
import sys
from queue import Queue
import threading
import time
import speech_recognition as sr
import pygame
from pynput import keyboard

# Проверяем и добавляем путь к проекту
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if current_dir not in sys.path:
    sys.path.append(current_dir)
    print(f"Добавлен путь: {current_dir}")

print(f"Текущая директория: {os.getcwd()}")
print(f"PYTHONPATH: {sys.path}")
print("Базовые импорты выполнены")

# Пошаговая проверка импортов
try:
    print("Попытка импорта speech_recognition...")
    import speech_recognition as sr
    print("speech_recognition успешно импортирован")
except Exception as e:
    print(f"ОШИБКА при импорте speech_recognition: {e}")
    print("Проверка установленных пакетов...")
    try:
        import pkg_resources
        installed_packages = [pkg.key for pkg in pkg_resources.working_set]
        print("Установленные пакеты:")
        print("\n".join(installed_packages))
    except:
        print("Не удалось получить список пакетов")
    
    print("\nПожалуйста, выполните следующие команды:")
    print("pip install SpeechRecognition")
    print("pip install pyaudio")
    sys.exit(1)

try:
    print("Проверка доступности микрофонов...")
    mics = sr.Microphone.list_microphone_names()
    print(f"Доступные микрофоны: {mics}")
except Exception as e:
    print(f"ОШИБКА при проверке микрофонов: {e}")
    print("\nПроверьте установку PyAudio:")
    print("pip install pyaudio")
    sys.exit(1)

class VoiceRecognition:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.command_queue = Queue()
        self.is_running = True
        self.is_voice_active = True
        self.command_processor = None
        
        # Инициализация звуков
        pygame.mixer.init()
        self.notification_sound = pygame.mixer.Sound("app/static/sounds/notification.mp3")
        
        # Настройка слушателя клавиатуры
        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        self.keyboard_listener.daemon = True
        
    def set_command_processor(self, processor):
        self.command_processor = processor

    def play_notification(self):
        self.notification_sound.play()

    def on_key_press(self, key):
        if key == keyboard.Key.f2:
            self.toggle_voice()

    def toggle_voice(self):
        self.is_voice_active = not self.is_voice_active
        if self.is_voice_active:
            print("Голосовое управление ВКЛЮЧЕНО")
            self.play_notification()
        else:
            print("Голосовое управление ВЫКЛЮЧЕНО")
        return self.is_voice_active

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
                        audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)
                        self.process_audio(audio)
                    except sr.WaitTimeoutError:
                        continue
                    except Exception as e:
                        print(f"Ошибка при прослушивании: {e}")
                        time.sleep(1)  # Добавляем задержку при ошибке
        except Exception as e:
            print(f"Критическая ошибка микрофона: {e}")
            self.is_running = False

    def process_audio(self, audio):
        try:
            command = self.recognizer.recognize_google(audio, language='ru-RU')
            if command and self.command_processor:
                print(f"Распознано: {command}")
                self.play_notification()
                self.command_processor.process_command(command.lower())
        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            print(f"Ошибка сервиса распознавания: {e}")

    def start(self):
        try:
            print("Запуск клавиатурного слушателя...")
            self.keyboard_listener.start()
            
            print("Запуск потока распознавания голоса...")
            self.voice_thread = threading.Thread(target=self.listen_voice)
            self.voice_thread.daemon = True
            self.voice_thread.start()
            
            print("Голосовое управление активировано")
            self.play_notification()
            
        except Exception as e:
            print(f"Ошибка при запуске voice recognition: {e}")
            raise

    def stop(self):
        self.is_running = False
        self.keyboard_listener.stop()

    def cleanup(self):
        print("Очистка ресурсов voice recognition...")
        self.is_running = False
        if hasattr(self, 'keyboard_listener'):
            self.keyboard_listener.stop()
        if hasattr(self, 'voice_thread'):
            self.voice_thread.join(timeout=1)
        pygame.mixer.quit()

print("Модуль voice_recognition.py загружен") 