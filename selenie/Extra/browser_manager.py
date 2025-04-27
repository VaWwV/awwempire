from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import time
import os
import psutil

class BrowserManager:
    def __init__(self):
        self.driver = None
        self.setup_logging()
        
    def setup_logging(self):
        """Настройка логирования"""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
    def open_browser(self):
        """Открывает браузер"""
        try:
            # Настройка Chromium
            chrome_options = Options()
            chrome_options.binary_location = r"G:\chrome\chrome.exe"
            
            # Используем существующий профиль work
            user_data_dir = r"C:\Users\Григорий\AppData\Local\Chromium\User Data"
            chrome_options.add_argument(f'--user-data-dir={user_data_dir}')
            chrome_options.add_argument('--profile-directory=work')
            
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
                self.logger.error(f"Ошибка при закрытии существующих процессов: {e}")
            
            # Проверяем существование файлов
            if not os.path.exists(r"G:\chrome\chrome.exe"):
                self.logger.error("Ошибка: Не найден файл браузера G:\chrome\chrome.exe")
                return False
                
            if not os.path.exists(r"G:\chromedriver\chromedriver-win64\chromedriver.exe"):
                self.logger.error("Ошибка: Не найден файл драйвера G:\chromedriver\chromedriver-win64\chromedriver.exe")
                return False
            
            # Оптимизированные настройки для производительности
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--autoplay-policy=no-user-gesture-required")
            chrome_options.add_argument("--disable-features=IsolateOrigins,site-per-process")
            chrome_options.add_argument("--disable-site-isolation-trials")
            chrome_options.add_argument("--ignore-gpu-blocklist")
            chrome_options.add_argument("--enable-gpu-rasterization")
            chrome_options.add_argument("--enable-zero-copy")
            chrome_options.add_argument("--enable-accelerated-video-decode")
            chrome_options.add_argument("--enable-accelerated-mjpeg-decode")
            chrome_options.add_argument("--disable-features=UseOzonePlatform")
            chrome_options.add_argument("--disable-software-rasterizer")
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-popup-blocking')
            chrome_options.add_argument('--disable-gpu-sandbox')
            chrome_options.add_argument('--no-default-browser-check')
            chrome_options.add_argument('--no-first-run')
            chrome_options.add_argument('--disable-notifications')
            
            # Экспериментальные опции
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option("useAutomationExtension", False)
            chrome_options.add_experimental_option("detach", True)
            
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
            chrome_options.add_experimental_option("prefs", prefs)

            try:
                service = Service(r'G:\chromedriver\chromedriver-win64\chromedriver.exe')
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                self.logger.info("Драйвер успешно создан")
            except Exception as e:
                self.logger.error(f"Ошибка при создании драйвера: {e}")
                return False
                
            if not self.driver:
                self.logger.error("Ошибка: драйвер не был инициализирован")
                return False
                
            try:
                # Скрываем факт автоматизации
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                    "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                })
                
                # Дополнительные оптимизации через CDP
                self.driver.execute_cdp_cmd('Network.enable', {})
                self.driver.execute_cdp_cmd('Network.setBypassServiceWorker', {'bypass': True})
                self.driver.execute_cdp_cmd('Page.enable', {})
                self.driver.execute_cdp_cmd('Page.setBypassCSP', {'enabled': True})
                
                self.logger.info("Автоматизация успешно настроена")
            except Exception as e:
                self.logger.error(f"Ошибка при настройке автоматизации: {e}")
            
            self.logger.info("Браузер успешно запущен с профилем work и оптимизацией производительности")
            return True
            
        except Exception as e:
            self.logger.error(f"Общая ошибка при запуске браузера: {e}")
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
            self.driver = None
            return False
            
    def close_browser(self):
        """Закрытие браузера"""
        try:
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
                self.logger.info("Браузер закрыт")
                
            # Завершаем все процессы Chromium
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if any(browser in proc.info['name'].lower() for browser in ['chrome', 'chromium']):
                        proc.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
                    
            time.sleep(1)  # Даем время на закрытие процессов
        except Exception as e:
            self.logger.error(f"Произошла ошибка при закрытии браузера: {str(e)}")
            
    def open_url(self, url):
        """Открывает указанный URL в браузере"""
        try:
            if not self.driver:
                if not self.open_browser():
                    return False
            self.driver.get(url)
            self.logger.info(f"Opened URL: {url}")
            return True
        except Exception as e:
            self.logger.error(f"Error opening URL: {e}")
            return False

    def scroll_up(self):
        """Прокрутка страницы вверх"""
        try:
            if self.driver:
                self.driver.execute_script("window.scrollBy(0, -500);")
                self.logger.info("Scrolled up")
                return True
        except Exception as e:
            self.logger.error(f"Error scrolling up: {e}")
            return False

    def scroll_down(self):
        """Прокрутка страницы вниз"""
        try:
            if self.driver:
                self.driver.execute_script("window.scrollBy(0, 500);")
                self.logger.info("Scrolled down")
                return True
        except Exception as e:
            self.logger.error(f"Error scrolling down: {e}")
            return False

    def refresh_page(self):
        """Обновление страницы"""
        try:
            if self.driver:
                self.driver.refresh()
                self.logger.info("Page refreshed")
                return True
        except Exception as e:
            self.logger.error(f"Error refreshing page: {e}")
            return False

    def focus_input(self, field_name):
        """Фокусировка на поле ввода"""
        try:
            if self.driver:
                input_field = self.driver.find_element("name", field_name)
                input_field.click()
                self.logger.info(f"Focused input field: {field_name}")
                return True
        except Exception as e:
            self.logger.error(f"Error focusing input field: {e}")
            return False

    def type_text(self, text):
        """Ввод текста в активное поле"""
        try:
            if self.driver:
                active_element = self.driver.switch_to.active_element
                active_element.send_keys(text)
                self.logger.info(f"Typed text: {text}")
                return True
        except Exception as e:
            self.logger.error(f"Error typing text: {e}")
            return False 