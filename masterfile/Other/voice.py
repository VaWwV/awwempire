import speech_recognition as sr
import subprocess
import tkinter as tk
from tkinter import messagebox
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

def start_app():
    try:
        print("Голосовой помощник Макарчик запущен.")
        print("Голосовое управление ВКЛЮЧЕНО")
        print("Скажите 'помощь' для просмотра списка доступных команд")

        # Запускаем Flask в отдельном потоке
        flask_thread = threading.Thread(target=start_flask)
        flask_thread.daemon = True
        flask_thread.start()

        # Даем время на запуск Flask
        time.sleep(2)

        # Запускаем прослушивание клавиатуры
        keyboard_listener = keyboard.Listener(on_press=on_key_press)
        keyboard_listener.daemon = True
        keyboard_listener.start()

        # Запускаем прослушивание в отдельном потоке
        listen_thread = threading.Thread(target=continuous_listen)
        listen_thread.daemon = True
        listen_thread.start()

        # Обрабатываем команды в основном потоке
        process_commands()
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

# Создаем графический интерфейс
def create_gui():
    root = tk.Tk()
    root.title("Голосовой помощник Макарчик")

    start_button = tk.Button(root, text="Запустить", command=start_app)
    start_button.pack(pady=20)

    stop_button = tk.Button(root, text="Остановить", command=root.quit)
    stop_button.pack(pady=10)

    root.mainloop()

# В конце файла, перед блоком if __name__ == "__main__":, добавьте вызов create_gui()
create_gui()


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
        try:
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
                if driver:  # Проверяем, что браузер успешно запущен
                    driver.get('https://www.youtube.com')
                    print("YouTube открыт после перезапуска браузера")
                else:
                    print("Не удалось перезапустить браузер")
            except Exception as e2:
                print(f"Критическая ошибка при перезапуске браузера: {e2}")
                driver = None
            
    except Exception as e:
        print(f"Общая ошибка при открытии YouTube: {e}")
        driver = None

def search_youtube(query):
    """Ищет видео на YouTube"""
    try:
        # Находим поле поиска
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "search_query"))
        )
        search_box.clear()
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        print(f"Ищу: {query}")
        
        # Ждем загрузки результатов
        time.sleep(2)
        
        # Показываем список видео
        print("\nНайденные видео:")
        videos = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ytd-video-renderer"))
        )
        
        # Выводим первые 5 видео
        for i, video in enumerate(videos[:5], 1):
            title = video.find_element(By.CSS_SELECTOR, "#video-title").text
            print(f"{i}. {title}")
        
        print("\nСкажите 'выбрать видео НОМЕР' для выбора видео")
        
    except Exception as e:
        print(f"Ошибка при поиске видео: {e}")

def convert_word_to_number(word):
    """Конвертирует число прописью в цифру"""
    numbers = {
        'один': 1, 'первый': 1, 'первое': 1,
        'два': 2, 'второй': 2, 'второе': 2,
        'три': 3, 'третий': 3, 'третье': 3,
        'четыре': 4, 'четвертый': 4, 'четвертое': 4,
        'пять': 5, 'пятый': 5, 'пятое': 5
    }
    return numbers.get(word.lower())

def select_video(number):
    """Выбирает видео по номеру из списка"""
    try:
        videos = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ytd-video-renderer"))
        )
        
        if 1 <= number <= len(videos):
            videos[number-1].find_element(By.CSS_SELECTOR, "#video-title").click()
            print(f"Открываю видео номер {number}")
        else:
            print("Неверный номер видео")
    except Exception as e:
        print(f"Ошибка при выборе видео: {e}")

def select_recommended_video(number=None, title=None):
    """Выбирает видео из рекомендаций по номеру или названию"""
    try:
        # Ждем загрузки рекомендованных видео
        videos = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ytd-rich-item-renderer"))
        )
        
        # Выводим список доступных видео
        print("\nДоступные видео:")
        for i, video in enumerate(videos[:10], 1):  # Увеличили до 10 видео
            try:
                video_title = video.find_element(By.CSS_SELECTOR, "#video-title").text
                print(f"{i}. {video_title}")
            except:
                continue

        if title:  # Если ищем по названию
            for video in videos:
                try:
                    video_title = video.find_element(By.CSS_SELECTOR, "#video-title").text
                    if title.lower() in video_title.lower():
                        driver.execute_script("arguments[0].scrollIntoView(true);", video)
                        time.sleep(0.5)
                        video.find_element(By.CSS_SELECTOR, "#video-title").click()
                        print(f"Открываю видео: {video_title}")
                        return
                except:
                    continue
            print("Видео с таким названием не найдено")
        elif number and 1 <= number <= len(videos):  # Если ищем по номеру
            driver.execute_script("arguments[0].scrollIntoView(true);", videos[number-1])
            time.sleep(0.5)
            videos[number-1].find_element(By.CSS_SELECTOR, "#video-title").click()
            print(f"Открываю видео номер {number}")
        else:
            print("Неверный номер видео")
    except Exception as e:
        print(f"Ошибка при выборе видео: {e}")

def select_search_video(number=None, title=None):
    """Выбирает видео из результатов поиска по номеру или названию"""
    try:
        videos = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ytd-video-renderer"))
        )
        
        # Выводим список найденных видео
        print("\nНайденные видео:")
        for i, video in enumerate(videos[:10], 1):  # Увеличили до 10 видео
            try:
                video_title = video.find_element(By.CSS_SELECTOR, "#video-title").text
                print(f"{i}. {video_title}")
            except:
                continue

        if title:  # Если ищем по названию
            for video in videos:
                try:
                    video_title = video.find_element(By.CSS_SELECTOR, "#video-title").text
                    if title.lower() in video_title.lower():
                        driver.execute_script("arguments[0].scrollIntoView(true);", video)
                        time.sleep(0.5)
                        video.find_element(By.CSS_SELECTOR, "#video-title").click()
                        print(f"Открываю видео: {video_title}")
                        return
                except:
                    continue
            print("Видео с таким названием не найдено")
        elif number and 1 <= number <= len(videos):  # Если ищем по номеру
            driver.execute_script("arguments[0].scrollIntoView(true);", videos[number-1])
            time.sleep(0.5)
            videos[number-1].find_element(By.CSS_SELECTOR, "#video-title").click()
            print(f"Открываю видео номер {number}")
        else:
            print("Неверный номер видео")
    except Exception as e:
        print(f"Ошибка при выборе видео: {e}")

def scroll_page(direction):
    """Прокручивает страницу вверх или вниз"""
    try:
        if direction == "вниз":
            driver.execute_script("window.scrollBy(0, 500);")
            print("Страница прокручена вниз")
        elif direction == "вверх":
            driver.execute_script("window.scrollBy(0, -500);")
            print("Страница прокручена вверх")
        elif direction == "начало":
            driver.execute_script("window.scrollTo(0, 0);")
            print("Страница прокручена в начало")
        elif direction == "конец":
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            print("Страница прокручена в конец")
    except Exception as e:
        print(f"Ошибка при прокрутке страницы: {e}")

def refresh_page():
    """Обновляет текущую страницу"""
    try:
        driver.refresh()
        print("Страница обновлена")
    except Exception as e:
        print(f"Ошибка при обновлении страницы: {e}")

def show_help():
    """Показывает список всех доступных команд"""
    print("\nСписок доступных голосовых команд:")
    print("Управление браузером:")
    print("- 'макарчик запускай' - запуск браузера")
    print("- 'макарчик закрывай' - закрытие браузера")
    print("- 'обнови страницу' - обновление текущей страницы")
    
    print("\nРабота с YouTube:")
    print("- 'открой youtube' - открытие YouTube")
    print("- 'найди видео НАЗВАНИЕ' - поиск видео на YouTube")
    print("- 'включи видео НОМЕР' - выбор видео из рекомендаций по номеру (1-10)")
    print("- 'включи видео НАЗВАНИЕ' - выбор видео из рекомендаций по названию")
    print("- 'включи видео поиск НОМЕР' - выбор видео из результатов поиска по номеру")
    print("- 'включи видео поиск НАЗВАНИЕ' - выбор видео из результатов поиска по названию")
    
    print("\nНавигация по странице:")
    print("- 'листай вверх' - прокрутка страницы вверх")
    print("- 'листай вниз' - прокрутка страницы вниз")
    print("- 'листай начало' - прокрутка в начало страницы")
    print("- 'листай конец' - прокрутка в конец страницы")
    
    print("\nРабота с полями ввода:")
    print("- 'ввод' - включение режима ввода текста в активное поле")
    print("- 'ввод в поле имя НАЗВАНИЕ' - включение режима ввода в поле по имени")
    print("- 'ввод в поле id НАЗВАНИЕ' - включение режима ввода в поле по id")
    print("- 'ввод в поле класс НАЗВАНИЕ' - включение режима ввода в поле по классу")
    print("- 'стоп ввод' - выключение режима ввода текста")
    
    print("\nУправление программой:")
    print("- 'помощь' - показать этот список команд")
    print("- 'микрофон' - выключение голосового управления")
    print("- 'стоп' - выход из программы")
    print("- F2 - включение/выключение голосового управления вручную")

def process_commands():
    global is_running, is_input_mode, current_input_field, is_voice_active
    while is_running:
        try:
            command = command_queue.get(timeout=0.1)
            print(f"Вы сказали: {command}")
            
            if "стоп" in command:
                close_browser()
                print("Выход из программы.")
                is_running = False
            elif "помощь" in command:
                show_help()
            elif "микрофон" in command:
                is_voice_active = False
                print("Голосовое управление ВЫКЛЮЧЕНО. Нажмите F2 для включения.")
            elif "макарчик запускай" in command:
                setup_browser()
            elif "макарчик закрывай" in command:
                close_browser()
            elif "открой youtube" in command:
                open_youtube()
            elif "обнови страницу" in command:
                refresh_page()
            elif command.startswith("листай"):
                direction = command.split()[-1]
                scroll_page(direction)
            elif command.startswith("найди видео"):
                search_query = command[11:].strip()
                if search_query:
                    search_youtube(search_query)
                else:
                    print("Скажите, что искать на YouTube")
            elif command.startswith("включи видео") or command.startswith("открой видео"):
                search_text = command[13:].strip()
                
                if search_text.isdigit() or any(num in search_text for num in ['первое', 'второе', 'третье', 'четвертое', 'пятое']):
                    if search_text.isdigit():
                        number = int(search_text)
                    else:
                        number = convert_word_to_number(search_text)
                    
                    if "поиск" in command:
                        select_search_video(number=number)
                    else:
                        select_recommended_video(number=number)
                else:
                    if "поиск" in command:
                        select_search_video(title=search_text)
                    else:
                        select_recommended_video(title=search_text)
            elif command.startswith("ввод в поле"):
                parts = command.split()
                if len(parts) >= 4:
                    field_type = parts[3]
                    field_value = " ".join(parts[4:])
                    field = find_input_field(field_type, field_value)
                    if field:
                        current_input_field = field
                        is_input_mode = True
                        print(f"Режим ввода включен для поля {field_value}. Говорите текст. Скажите 'стоп ввод' для выхода.")
                    else:
                        print(f"Поле {field_value} не найдено")
            elif command == "ввод":
                is_input_mode = True
                current_input_field = None
                print("Режим ввода включен. Говорите текст. Скажите 'стоп ввод' для выхода из режима ввода.")
            else:
                print(f"Неизвестная команда: {command}")
                print("Скажите 'помощь' для просмотра списка доступных команд")
        except Empty:
            continue

def start_flask():
    app.run(debug=False)

if __name__ == "__main__":
    print("Голосовой помощник Макарчик запущен.")
    print("Голосовое управление ВКЛЮЧЕНО")
    print("Скажите 'помощь' для просмотра списка доступных команд")
    
    try:
        # Запускаем Flask в отдельном потоке
        flask_thread = threading.Thread(target=start_flask)
        flask_thread.daemon = True
        flask_thread.start()
        
        # Даем время на запуск Flask
        time.sleep(2)
        
        # Запускаем прослушивание клавиатуры
        keyboard_listener = keyboard.Listener(on_press=on_key_press)
        keyboard_listener.daemon = True
        keyboard_listener.start()
        
        # Запускаем прослушивание в отдельном потоке
        listen_thread = threading.Thread(target=continuous_listen)
        listen_thread.daemon = True
        listen_thread.start()
        
        # Обрабатываем команды в основном потоке
        process_commands()
    except KeyboardInterrupt:
        print("\nПрограмма остановлена пользователем")
    except Exception as e:
        print(f"Критическая ошибка: {e}")
    finally:
        is_running = False
        close_browser()
        sys.exit(0)
