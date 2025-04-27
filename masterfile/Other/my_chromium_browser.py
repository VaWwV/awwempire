from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import os

# Укажи путь к исполняемому файлу Chromium WebDriver
chromium_driver_path = r'G:\chromedriver\chromedriver-win64\chromedriver.exe'

# Укажи путь к исполняемому файлу Chromium
chromium_binary_path = r'G:\chromedriver\chromedrive\chrome.exe'
# Укажите путь к файлу расширения
adblock_extension_path = r'G:\path\to\adblock.crx'

#Проверка существования файла расширения
if not os.path.exists(adblock_extension_path):
    raise FileNotFoundError(f"Path to the extension doesn't exist: {adblock_extension_path}")

# Настройка WebDriver
service = Service(chromium_driver_path)
options = webdriver.ChromeOptions()
options.binary_location = chromium_binary_path

# Отключение песочницы (sandbox) для Chromium
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
# Добавление расширений
options.add_extension(adblock_extension_path)

# Настройка автоматической работы на false
options.add_argument('--disable-background-networking')
options.add_argument('--disable-background-timer-throttling')
options.add_argument('--disable-backgrounding-occluded-windows')
options.add_argument('--disable-breakpad')
options.add_argument('--disable-client-side-phishing-detection')
options.add_argument('--disable-default-apps')
# options.add_argument('--disable-extensions')  # Убрал этот аргумент
options.add_argument('--disable-features=TranslateUI')
options.add_argument('--disable-hang-monitor')
options.add_argument('--disable-ipc-flooding-protection')
options.add_argument('--disable-popup-blocking')
options.add_argument('--disable-prompt-on-repost')
options.add_argument('--disable-sync')
options.add_argument('--disable-web-resources')
options.add_argument('--enable-automation')
options.add_argument('--password-store=basic')
options.add_argument('--use-gl=swiftshader')

driver = webdriver.Chrome(service=service, options=options)

# Открытие Google.com
driver.get("https://www.google.com")

# Вывод заголовка страницы
print(driver.title)

# Закрытие браузера
driver.quit()
