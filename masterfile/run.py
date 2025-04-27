import sys
import os
import logging
import threading
import time
from pynput import keyboard
from webdriver_manager.chrome import ChromeDriverManager
from app.browser_manager import BrowserManager
from app.voice_recognition import VoiceRecognition
from app.youtube_controller import YouTubeController
from app.command_processor import CommandProcessor
from app import app, socketio

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def print_diagnostic_info():
    logger.info("=== Диагностическая информация ===")
    logger.info(f"Текущая директория: {os.getcwd()}")
    logger.info(f"Путь к Python: {sys.executable}")
    logger.info(f"PYTHONPATH: {sys.path}")
    logger.info(f"Аргументы запуска: {sys.argv}")
    logger.info("===============================")

def start_flask():
    socketio.run(app, debug=False, use_reloader=False, port=5000)

def main():
    print_diagnostic_info()
    logger.info("Запуск программы...")

    try:
        logger.info("Инициализация компонентов...")
        
        # Инициализация компонентов
        browser_manager = BrowserManager()
        voice_recognition = VoiceRecognition()
        youtube_controller = YouTubeController(browser_manager)
        command_processor = CommandProcessor(browser_manager, voice_recognition, youtube_controller)
        
        # Настройка обработчика команд
        voice_recognition.set_command_processor(command_processor)
        
        # Запуск Flask в отдельном потоке
        flask_thread = threading.Thread(target=start_flask, daemon=True)
        flask_thread.start()
        
        # Запуск голосового помощника
        logger.info("Запуск голосового помощника...")
        voice_recognition.start()
        
        # Бесконечный цикл для поддержания работы программы
        while True:
            time.sleep(0.1)
    except Exception as e:
        logger.critical(f"Критическая ошибка: {e}", exc_info=True)
        if 'voice_recognition' in locals():
            voice_recognition.cleanup()
        if 'browser_manager' in locals():
            browser_manager.close_browser()
    finally:
        logger.info("Завершение работы...")
        if 'voice_recognition' in locals():
            voice_recognition.cleanup()
        if 'browser_manager' in locals():
            browser_manager.close_browser()
        logger.info("Программа завершена")

if __name__ == "__main__":
    main()