import logging
import os
import sys
from queue import Queue
import threading
import time
import speech_recognition as sr
import pygame
from pynput import keyboard

class VoiceRecognition:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.command_queue = Queue()
        self.is_running = True
        self.is_voice_active = True
        self.command_processor = None
        
        pygame.mixer.init()
        self.notification_sound = pygame.mixer.Sound("app/static/sounds/notification.mp3")
        
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
            self.logger.info("Голосовое управление ВКЛЮЧЕНО")
            self.play_notification()
        else:
            self.logger.info("Голосовое управление ВЫКЛЮЧЕНО")
        return self.is_voice_active

    def listen_voice(self):
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
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
                        self.logger.error(f"Ошибка при прослушивании: {e}")
                        time.sleep(1)
        except Exception as e:
            self.logger.error(f"Критическая ошибка микрофона: {e}")
            self.is_running = False

    def process_audio(self, audio):
        try:
            command = self.recognizer.recognize_google(audio, language='ru-RU')
            if command and self.command_processor:
                self.logger.info(f"Распознано: {command}")
                self.play_notification()
                self.command_processor.process_command(command.lower())
        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            self.logger.error(f"Ошибка сервиса распознавания: {e}")

    def start(self):
        try:
            self.keyboard_listener.start()
            self.voice_thread = threading.Thread(target=self.listen_voice)
            self.voice_thread.daemon = True
            self.voice_thread.start()
            self.logger.info("Голосовое управление активировано")
            self.play_notification()
        except Exception as e:
            self.logger.error(f"Ошибка при запуске voice recognition: {e}")
            raise

    def stop(self):
        self.is_running = False
        self.keyboard_listener.stop()

    def cleanup(self):
        self.is_running = False
        if hasattr(self, 'keyboard_listener'):
            self.keyboard_listener.stop()
        if hasattr(self, 'voice_thread'):
            self.voice_thread.join(timeout=1)
        pygame.mixer.quit()