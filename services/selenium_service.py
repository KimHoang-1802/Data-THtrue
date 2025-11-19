# services/selenium_service.py


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from utils.logger import get_logger
import time

logger = get_logger("selenium")

class SeleniumService:

    def __init__(self, headless=True):
        options = Options()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")

        self.driver = webdriver.Chrome(options=options)
        logger.info("Khởi tạo Selenium thành công")

    def get_page(self, url, wait=2):
        logger.info(f"Tải trang: {url}")
        self.driver.get(url)
        time.sleep(wait)

    def scroll_to_bottom(self, pause=0.5, max_scrolls=5):
        logger.info("Bắt đầu scroll...")
        for _ in range(max_scrolls):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(pause)

    def quit(self):
        logger.info("Đóng Selenium driver")
        self.driver.quit()
