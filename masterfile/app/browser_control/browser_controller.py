from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

class BrowserController:
    def __init__(self, port):
        self.port = port
        self.driver = self._get_driver()

    def _get_driver(self):
        options = webdriver.ChromeOptions()
        options.debugger_address = f"127.0.0.1:{self.port}"
        service = Service()  # Укажите путь к chromedriver, если необходимо
        driver = webdriver.Chrome(service=service, options=options)
        return driver

    def navigate_to(self, url):
        self.driver.get(url)

    def get_page_title(self):
        return self.driver.title

    def close_browser(self):
        self.driver.quit()