import logging
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException

class BrowserManager:
    def __init__(self):
        self.driver = None
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

    def setup_browser(self):
        """Инициализация браузера Chrome"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            driver_path = ChromeDriverManager().install()
            if not os.path.exists(driver_path):
                self.logger.error(f"ChromeDriver не найден по пути: {driver_path}")
                return False
                
            service = Service(driver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.logger.info("Браузер Chrome успешно инициализирован")
            return True
            
        except WebDriverException as e:
            self.logger.exception("WebDriver error:")
            return False
        except Exception as e:
            self.logger.exception("Ошибка при создании браузера:")
            return False

    def open_browser(self):
        """Открытие браузера"""
        try:
            if self.driver:
                self.logger.info("Браузер уже запущен")
                return True
                
            success = self.setup_browser()
            if success:
                self.logger.info("Браузер успешно запущен")
                return True
            else:
                self.logger.error("Не удалось запустить браузер")
                return False
                
        except Exception as e:
            self.logger.exception("Ошибка открытия браузера:")
            return False

    def open_url(self, url):
        """Открытие указанного URL"""
        try:
            if not self.driver:
                self.logger.info("Браузер не инициализирован, пытаюсь запустить...")
                if not self.setup_browser():
                    self.logger.error("Не удалось инициализировать браузер")
                    return False
            
            self.logger.info(f"Открываю URL: {url}")
            self.driver.get(url)
            self.logger.info(f"URL {url} успешно открыт")
            return True
            
        except Exception as e:
            self.logger.exception("Ошибка открытия URL:")
            return False

    def close_browser(self):
        """Закрытие браузера"""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
                self.logger.info("Браузер успешно закрыт")
            except Exception as e:
                self.logger.exception("Ошибка закрытия браузера:")

    def get_driver(self):
        """Получение текущего драйвера"""
        return self.driver