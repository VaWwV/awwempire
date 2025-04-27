import sys
import os
print("=== Тест импортов ===")
print(f"Python: {sys.executable}")
print(f"Директория: {os.getcwd()}")

try:
    print("\nПроверка speech_recognition...")
    import speech_recognition as sr
    print("OK: speech_recognition импортирован")
except Exception as e:
    print(f"ОШИБКА: speech_recognition - {e}")

try:
    print("\nПроверка pyaudio...")
    import pyaudio
    print("OK: pyaudio импортирован")
except Exception as e:
    print(f"ОШИБКА: pyaudio - {e}")

try:
    print("\nПроверка pygame...")
    import pygame
    print("OK: pygame импортирован")
except Exception as e:
    print(f"ОШИБКА: pygame - {e}")

print("\nПроверка локального модуля...")
try:
    from app.voice_recognition import VoiceRecognition
    print("OK: voice_recognition импортирован")
except Exception as e:
    print(f"ОШИБКА: voice_recognition - {e}")

print("\nТест завершен")
input("Нажмите Enter для выхода...") 