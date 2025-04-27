import speech_recognition as sr
import subprocess
import sys
import psutil
import threading
import time
from queue import Queue, Empty
import pygame
from flask import Flask, render_template
from Chromium_Browser import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pynput import keyboard
import os

# Инициализация Flask
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    return 'Данные отправлены!'

# Инициализация pygame для звука
pygame.mixer.init()
notification_sound = pygame.mixer.Sound("icq.mp3")

# Инициализация распознавателя
recognizer = sr.Recognizer()

# Глобальные переменные
driver = None
command_queue = Queue()
is_running = True
is_input_mode = False
is_voice_active = True  # Теперь голосовое управление включено по умолчанию
current_input_field = None  # Текущее поле ввода

def play_notification():
    notification_sound.play()

def setup_browser():
    global driver
    try:
        # Настройка Chromium
        chromium_options = Options()
        chromium_options.binary_location = r"G:\chrome\chrome.exe"

        # Используем существующий профиль work
        user_data_dir = r"C:\Users\Григорий\AppData\Local\Chromium\User Data"
        chromium_options.add_argument(f'--user-data-dir={user_data_dir}')
        chromium_options.add_argument('--profile-directory=work')

        # Отключаем существующие процессы Chromium перед запуском
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if any(browser in proc.info['name'].lower() for browser in ['chrome', 'chromium']):
                        proc.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            time.sleep(1)
        except Exception as e:
            print(f"Ошибка при закрытии существующих процессов: {e}")

        # Проверяем существование файлов
        if not os.path.exists(r"G:\chrome\chrome.exe"):
            print("Ошибка: Не найден файл браузера G:\chrome\chrome.exe")
            return False

        if not os.path.exists(r"G:\chromedriver\chromedriver-win64\chromedriver.exe"):
            print("Ошибка: Не найден файл драйвера G:\chromedriver\chromedriver-win64\chromedriver.exe")
            return False

        # Оптимизированные настройки для производительности
        chromium_options.add_argument("--disable-blink-features=AutomationControlled")
        chromium_options.add_argument("--start-maximized")
        chromium_options.add_argument("--autoplay-policy=no-user-gesture-required")  # Разрешаем автовоспроизведение
        chromium_options.add_argument("--disable-features=IsolateOrigins,site-per-process")  # Отключаем изоляцию процессов
        chromium_options.add_argument("--disable-site-isolation-trials")  # Отключаем изоляцию сайтов
        chromium_options.add_argument("--ignore-gpu-blocklist")  # Игнорируем блоклист GPU
        chromium_options.add_argument("--enable-gpu-rasterization")  # Включаем GPU растеризацию
        chromium_options.add_argument("--enable-zero-copy")  # Включаем zero-copy
        chromium_options.add_argument("--enable-accelerated-video-decode")  # Включаем аппаратное ускорение видео
        chromium_options.add_argument("--enable-accelerated-mjpeg-decode")  # Включаем аппаратное ускорение MJPEG
        chromium_options.add_argument("--disable-features=UseOzonePlatform")  # Отключаем Ozone
        chromium_options.add_argument("--disable-software-rasterizer")  # Отключаем программный растеризатор
        chromium_options.add_argument('--disable-dev-shm-usage')
        chromium_options.add_argument('--no-sandbox')
        chromium_options.add_argument('--disable-popup-blocking')
        chromium_options.add_argument('--disable-gpu-sandbox')
        chromium_options.add_argument('--no-default-browser-check')
        chromium_options.add_argument('--no-first-run')
        chromium_options.add_argument('--disable-notifications')

        # Экспериментальные опции
        chromium_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chromium_options.add_experimental_option("useAutomationExtension", False)
        chromium_options.add_experimental_option("detach", True)

        # Настройки производительности через preferences
        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "profile.managed_default_content_settings.images": 1,
            "profile.managed_default_content_settings.javascript": 1,
            "profile.managed_default_content_settings.cookies": 1,
            "profile.managed_default_content_settings.plugins": 1,
            "profile.managed_default_content_settings.popups": 2,
            "profile.managed_default_content_settings.geolocation": 2,
            "profile.managed_default_content_settings.media_stream": 2,
            "hardware_acceleration_mode.enabled": True,
            "profile.password_manager_enabled": False,
            "profile.default_content_settings.popups": 0,
            "download_restrictions": 3
        }
        chromium_options.add_experimental_option("prefs", prefs)

        try:
            service = Service(r'G:\chromedriver\chromedriver-win64\chromedriver.exe')
            driver = webdriver.Chrome(service=service, options=chromium_options)
            print("Драйвер успешно создан")
        except Exception as e:
            print(f"Ошибка при создании драйвера: {e}")
            return False

        if not driver:
            print("Ошибка: драйвер не был инициализирован")
            return False

        try:
            # Скрываем факт автоматизации
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})

            # Дополнительные оптимизации через CDP
            driver.execute_cdp_cmd('Network.enable', {})
            driver.execute_cdp_cmd('Network.setBypassServiceWorker', {'bypass': True})
            driver.execute_cdp_cmd('Page.enable', {})
            driver.execute_cdp_cmd('Page.setBypassCSP', {'enabled': True})

            print("Автоматизация успешно настроена")
        except Exception as e:
            print(f"Ошибка при настройке автоматизации: {e}")
            # Продолжаем работу, так как это некритичная ошибка

        print("Браузер успешно запущен с профилем work и оптимизацией производительности")
        return True

    except Exception as e:
        print(f"Общая ошибка при запуске браузера: {e}")
        if driver:
            try:
                driver.quit()
            except:
                pass
        driver = None
        return False

def find_input_field(field_type, value):
    """Находит поле ввода на странице"""
    try:
        if field_type == "name":
            return driver.find_element(By.NAME, value)
        elif field_type == "id":
            return driver.find_element(By.ID, value)
        elif field_type == "class":
            return driver.find_element(By.CLASS_NAME, value)
        elif field_type == "xpath":
            return driver.find_element(By.XPATH, value)
    except Exception as e:
        print(f"Ошибка при поиске поля: {e}")
        return None

def input_text_to_field(text, field=None):
    """Вводит текст в указанное поле или активное поле"""
    try:
        if field:
            input_field = field
        else:
            input_field = driver.switch_to.active_element

        input_field.clear()
        input_field.send_keys(text)
        print(f"Введен текст: {text}")
    except Exception as e:
        print(f"Ошибка при вводе текста: {e}")

def close_browser():
    global driver
    try:
        if driver:
            try:
                driver.quit()
            except:
                pass
            driver = None
            print("Браузер закрыт")

        # Завершаем все процессы Chromium
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if any(browser in proc.info['name'].lower() for browser in ['chrome', 'chromium']):
                    proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        time.sleep(1)  # Даем время на закрытие процессов
    except Exception as e:
        print(f"Произошла ошибка при закрытии браузера: {str(e)}")

def on_key_press(key):
    global is_voice_active, is_input_mode
    try:
        if key == keyboard.Key.f2:
            is_voice_active = not is_voice_active
            is_input_mode = False
            if is_voice_active:
                print("Голосовое управление ВКЛЮЧЕНО")
                play_notification()
            else:
                print("Голосовое управление ВЫКЛЮЧЕНО")
    except AttributeError:
        pass

def continuous_listen():
    global is_running, is_input_mode, is_voice_active, current_input_field
    print("Инициализация микрофона...")

    try:
        mic = sr.Microphone()
        with mic as source:
            print("Настройка уровня шума...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            print("Слушаю...")

            while is_running:
                if not is_voice_active:
                    time.sleep(0.1)
                    continue

                try:
                    audio = recognizer.listen(source, timeout=0.5, phrase_time_limit=3)
                    command = recognizer.recognize_google(audio, language='ru-RU')
                    if command:
                        play_notification()
                        if is_input_mode:
                            if command.lower() == "стоп ввод":
                                is_input_mode = False
                                current_input_field = None
                                print("Режим ввода выключен")
                            else:
                                input_text_to_field(command, current_input_field)
                        else:
                            command_queue.put(command.lower())
                            print(f"Распознано: {command}")
                except sr.UnknownValueError:
                    continue
                except sr.RequestError as e:
                    print(f"Ошибка сервиса распознавания: {e}")
                    time.sleep(1)
                    continue
                except sr.WaitTimeoutError:
                    continue
                except Exception as e:
                    print(f"Ошибка при прослушивании: {e}")
                    time.sleep(1)
                    continue
    except Exception as e:
        print(f"Критическая ошибка микрофона: {e}")
        is_running = False

def open_youtube():
    """Открывает YouTube"""
    global driver
    try:
        # Если браузер не запущен или произошла ошибка, запускаем его заново
        if not driver:
            setup_browser()
            if not driver:  # Если после setup_browser driver все еще None
                print("Не удалось запустить браузер")
                return

        try:
            # Проверяем, открыт ли уже YouTube
            current_url = driver.current_url
            if not current_url.startswith('https://www.youtube.com'):
                driver.get('https://www.youtube.com')
                print("YouTube открыт")
            else:
                print("YouTube уже открыт")
        except Exception as e:
            print(f"Ошибка при проверке URL: {e}")
            # Перезапускаем браузер при ошибке
            try:
                if driver:
                    driver.quit()
                driver = None
                setup_browser()
            except Exception as e:
                print(f"Ошибка при перезапуске браузера: {e}")
    except Exception as e:
        print(f"Ошибка при открытии YouTube: {e}")

# Пример использования
if __name__ == "__main__":
    # Запуск Flask приложения
    app.run(debug=True)

    # Запуск голосового управления в отдельном потоке
    listen_thread = threading.Thread(target=continuous_listen)
    listen_thread.start()

    # Запуск обработки команд в отдельном потоке
    def command_handler():
        global is_running
        while is_running:
            try:
                command = command_queue.get(timeout=1)
                if command == "открыть youtube":
                    open_youtube()
                elif command == "закрыть браузер":
                    close_browser()
                    is_running = False
                # Добавьте другие команды по мере необходимости
            except Empty:
                continue

    command_thread = threading.Thread(target=command_handler)
    command_thread.start()

    # Запуск обработки нажатий клавиш в отдельном потоке
    with keyboard.Listener(on_press=on_key_press) as listener:
        listener.join()

