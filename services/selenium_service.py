# # services/selenium_service.py
# Vai trò: Điều khiển trình duyệt Chrome để tải trang web
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
        options.add_argument("--window-size=1920,1080")  # Thêm size cho headless

        self.driver = webdriver.Chrome(options=options)
        logger.info("Khởi tạo Selenium thành công")

    def get_page(self, url, wait=2):
        logger.info(f"Tải trang: {url}")
        self.driver.get(url)
        time.sleep(wait)

    def scroll_to_bottom(self, pause=0.5, max_scrolls=5):
        """
        Scroll xuống dần để lazy load toàn bộ sản phẩm
        Kiểm tra xem đã scroll hết chưa
        """
        logger.info(f"Bắt đầu scroll (max: {max_scrolls} lần)...")
        
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scroll_count = 0
        
        for i in range(max_scrolls):
            # Scroll xuống cuối
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(pause)
            
            # Tính chiều cao mới
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_count += 1
            
            # Nếu không còn load thêm nội dung thì dừng
            if new_height == last_height:
                logger.info(f"Đã scroll hết sau {scroll_count} lần")
                break
                
            last_height = new_height
        
        # Scroll lên một chút để đảm bảo tất cả ảnh được load
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 500);")
        time.sleep(0.5)

    def quit(self):
        logger.info("Đóng Selenium driver")
        self.driver.quit()