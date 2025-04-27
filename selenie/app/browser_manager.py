print("Загрузка browser_manager.py")

import logging
import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException

class BrowserManager:
    def __init__(self):
        print("Инициализация BrowserManager...")
        self.driver = None
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        print("BrowserManager инициализирован")

    def setup_browser(self):
        """Инициализация браузера Chrome"""
        try:
            print("Настройка браузера Chrome...")
            
            # Настройка опций Chrome
            chrome_options = Options()
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            # Получение пути к ChromeDriver
            driver_path = ChromeDriverManager().install()
            print(f"ChromeDriver path: {driver_path}")
            
            # Проверка существования файла драйвера
            if not os.path.exists(driver_path):
                print(f"ERROR: ChromeDriver не найден по пути: {driver_path}")
                return False
                
            # Создание сервиса
            print("Создание сервиса ChromeDriver...")
            service = Service(driver_path)
            
            # Создание драйвера
            print("Создание экземпляра веб-драйвера...")
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            print("Браузер Chrome успешно инициализирован")
            return True
            
        except WebDriverException as e:
            print(f"Ошибка WebDriver: {str(e)}")
            self.logger.exception("WebDriver error:")
            return False
        except Exception as e:
            print(f"Общая ошибка: {str(e)}")
            print(f"Тип ошибки: {type(e).__name__}")
            self.logger.exception("Ошибка при создании браузера:")
            return False

    def open_browser(self):
        """Открытие браузера"""
        try:
            if self.driver:
                print("Браузер уже запущен")
                return True
                
            print("Запуск нового браузера...")
            success = self.setup_browser()
            if success:
                print("Браузер успешно запущен")
                return True
            else:
                print("Не удалось запустить браузер")
                return False
                
        except Exception as e:
            print(f"Ошибка при открытии браузера: {e}")
            self.logger.exception("Ошибка открытия браузера:")
            return False

    def open_url(self, url):
        """Открытие указанного URL"""
        try:
            if not self.driver:
                print("Браузер не инициализирован, пытаюсь запустить...")
                if not self.setup_browser():
                    print("Не удалось инициализировать браузер")
                    return False
            
            print(f"Открываю URL: {url}")
            self.driver.get(url)
            print(f"URL {url} успешно открыт")
            return True
            
        except Exception as e:
            print(f"Ошибка при открытии URL {url}: {e}")
            self.logger.exception("Ошибка открытия URL:")
            return False

    def close_browser(self):
        """Закрытие браузера"""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
                print("Браузер успешно закрыт")
            except Exception as e:
                print(f"Ошибка при закрытии браузера: {e}")
                self.logger.exception("Ошибка закрытия браузера:")

    def get_driver(self):
        """Получение текущего драйвера"""
        return self.driver

    def get_chrome_version(self):
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
            version, _ = winreg.QueryValueEx(key, "version")
            return version
        except:
            return "Не удалось определить версию"

print("Модуль browser_manager.py загружен") 