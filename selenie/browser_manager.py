from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import psutil
import time
import os

class BrowserManager:
    def __init__(self):
        self.driver = None
        
    def setup_browser(self):
        try:
            chromium_options = Options()
            chromium_options.binary_location = r"G:\chrome\chrome.exe"
            
            user_data_dir = r"C:\Users\Григорий\AppData\Local\Chromium\User Data"
            chromium_options.add_argument(f'--user-data-dir={user_data_dir}')
            chromium_options.add_argument('--profile-directory=work')
            
            self._kill_existing_processes()
            
            if not self._check_files():
                return False
            
            self._setup_browser_options(chromium_options)
            
            if not self._create_driver(chromium_options):
                return False
                
            self._setup_automation()
            
            print("Браузер успешно запущен с профилем work и оптимизацией производительности")
            return True
            
        except Exception as e:
            print(f"Общая ошибка при запуске браузера: {e}")
            self.close_browser()
            return False
            
    def _kill_existing_processes(self):
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
            
    def _check_files(self):
        if not os.path.exists(r"G:\chrome\chrome.exe"):
            print("Ошибка: Не найден файл браузера G:\chrome\chrome.exe")
            return False
            
        if not os.path.exists(r"G:\chromedriver\chromedriver-win64\chromedriver.exe"):
            print("Ошибка: Не найден файл драйвера G:\chromedriver\chromedriver-win64\chromedriver.exe")
            return False
            
        return True
        
    def _setup_browser_options(self, options):
        # Оптимизированные настройки для производительности
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--start-maximized")
        options.add_argument("--autoplay-policy=no-user-gesture-required")
        options.add_argument("--disable-features=IsolateOrigins,site-per-process")
        options.add_argument("--disable-site-isolation-trials")
        options.add_argument("--ignore-gpu-blocklist")
        options.add_argument("--enable-gpu-rasterization")
        options.add_argument("--enable-zero-copy")
        options.add_argument("--enable-accelerated-video-decode")
        options.add_argument("--enable-accelerated-mjpeg-decode")
        options.add_argument("--disable-features=UseOzonePlatform")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-gpu-sandbox')
        options.add_argument('--no-default-browser-check')
        options.add_argument('--no-first-run')
        options.add_argument('--disable-notifications')
        
        # Экспериментальные опции
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("detach", True)
        
        # Настройки производительности
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
        options.add_experimental_option("prefs", prefs)
        
    def _create_driver(self, options):
        try:
            service = Service(r'G:\chromedriver\chromedriver-win64\chromedriver.exe')
            self.driver = webdriver.Chrome(service=service, options=options)
            print("Драйвер успешно создан")
            return True
        except Exception as e:
            print(f"Ошибка при создании драйвера: {e}")
            return False
            
    def _setup_automation(self):
        try:
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            self.driver.execute_cdp_cmd('Network.enable', {})
            self.driver.execute_cdp_cmd('Network.setBypassServiceWorker', {'bypass': True})
            self.driver.execute_cdp_cmd('Page.enable', {})
            self.driver.execute_cdp_cmd('Page.setBypassCSP', {'enabled': True})
            
            print("Автоматизация успешно настроена")
        except Exception as e:
            print(f"Ошибка при настройке автоматизации: {e}")
            
    def close_browser(self):
        try:
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
                print("Браузер закрыт")
                
            self._kill_existing_processes()
        except Exception as e:
            print(f"Произошла ошибка при закрытии браузера: {str(e)}")
            
    def get_driver(self):
        return self.driver 