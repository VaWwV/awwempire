from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging

class YouTubeController:
    def __init__(self, browser_manager):
        self.browser_manager = browser_manager
        self.wait_timeout = 5
        
    def open_youtube(self):
        try:
            return self.browser_manager.open_url('https://www.youtube.com')
        except Exception as e:
            logging.error(f"Error opening YouTube: {e}")
            return False

    def search_youtube(self, query):
        try:
            self.open_youtube()
            
            search_box = WebDriverWait(self.browser_manager.driver, self.wait_timeout).until(
                EC.presence_of_element_located((By.NAME, "search_query"))
            )
            
            search_box.clear()
            search_box.send_keys(query)
            search_box.submit()
            
            time.sleep(1)
            
            WebDriverWait(self.browser_manager.driver, self.wait_timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "ytd-video-renderer"))
            )
            
            return True
        except Exception as e:
            logging.error(f"Error searching YouTube: {e}")
            return False

    def select_video(self, number):
        try:
            videos = WebDriverWait(self.browser_manager.driver, self.wait_timeout).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ytd-video-renderer"))
            )
            
            if 0 < number <= len(videos):
                videos[number - 1].click()
                time.sleep(0.2)
                return True
            return False
        except Exception as e:
            logging.error(f"Error selecting video: {e}")
            return False

    def next_video(self):
        try:
            next_button = WebDriverWait(self.browser_manager.driver, self.wait_timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a.ytp-next-button"))
            )
            next_button.click()
            time.sleep(0.2)
            return True
        except Exception as e:
            logging.error(f"Error going to next video: {e}")
            return False

    def previous_video(self):
        try:
            self.browser_manager.driver.back()
            time.sleep(0.2)
            return True
        except Exception as e:
            logging.error(f"Error going to previous video: {e}")
            return False